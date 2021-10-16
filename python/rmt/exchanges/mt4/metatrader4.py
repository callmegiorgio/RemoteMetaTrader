import zmq
import json
import logging
import rmt
from datetime import datetime
from typing   import Dict, List, Optional, Set, Tuple
from time     import sleep
from rmt      import (Order, Side, OrderType,
                      Exchange, Tick, Bar, OrderStatus,
                      Timeframe, Instrument, Account)
from . import *

class MetaTrader4(Exchange):
    """Bindings for executing market operations on MetaTrader 4."""

    def __init__(self,
                 protocol: str = 'tcp',
                 host:     str = 'localhost',
                 req_port: int = 32768,
                 sub_port: int = 32769
    ):
        super().__init__()

        ctx = zmq.Context.instance()
        self._req_socket = ctx.socket(zmq.REQ)
        self._sub_socket = ctx.socket(zmq.SUB)

        ################################################################################
        # Set the REP socket to wait for at most 30 seconds to send requests and at most
        # 10 seconds to receive responses.
        #
        # This allows this Client to work well with the Expert Server when it is being
        # run by the MT4 Strategy Tester.
        #
        # If the Strategy Tester is running the Expert Server on visual mode with a low
        # speed, that will make the Tester invoke the Expert's `OnTick()` function very
        # slowly, which will in turn slow down any calls to ZMQ socket functions on the
        # Expert's end, and thus effectively reduce its receipt of Client's requests.
        # 
        # According to my measures, it seems that when set to the slowest possible speed,
        # the Strategy Tester has a delay of 24 seconds between calls to `OnTick()`, so
        # a value of 30 milliseconds to `zmq.SNDTIMEO` should suffice.
        # 
        # Since `OnTimer()` doesn't work while testing, this seems the only way to make
        # this work. Otherwise, the Client will keep raising `error.RequestTimeout`.
        #
        # The receive timeout, on the other hand, is not affected by the Strategy Tester
        # in any way. It is set here nonetheless just in case connection with the Expert
        # drops, in which case a request won't take forever to complete. 10 milliseconds
        # should be more than enough for that. But maybe turn this into a parameter for
        # `__init__()`?
        ################################################################################
        self._req_socket.setsockopt(zmq.SNDTIMEO, 30000)
        self._req_socket.setsockopt(zmq.RCVTIMEO, 10000)

        self._sub_socket.subscribe('orderPlaced')
        self._sub_socket.subscribe('orderFinished')
        self._sub_socket.subscribe('orderModified')
        self._sub_socket.subscribe('orderUpdated')

        self._subscribed_symbols: Set[str] = set()
        self._logger = logging.getLogger(MetaTrader4.__name__)

        self._account: Optional[Account] = None

        self._instruments: Dict[str, Instrument] = {}

        self._orders: Dict[int, Optional[Order]] = {}
        """Dictionary of tracked orders, mapped by ticket.
        
        No entry in the dictionary means an order is not tracked.

        Values of None in the dictionary mean that an order is tracked for event
        emitting purposes, but there's no order data other than its ticket.

        Having an order object stored means we got order data from the server.
        """

        self._event_dispatcher = events.Dispatcher()
        self._event_dispatcher.register('tick',          events.TickEvent,          self._on_tick_event)
        self._event_dispatcher.register('orderPlaced',   events.OrderPlacedEvent,   self._on_order_placed_event)
        self._event_dispatcher.register('orderFinished', events.OrderFinishedEvent, self._on_order_finished_event)
        self._event_dispatcher.register('orderModified', events.OrderModifiedEvent, self._on_order_modified_event)
        self._event_dispatcher.register('orderUpdated',  events.OrderUpdatedEvent,  self._on_order_updated_event)

        self.connect(protocol, host, req_port, sub_port)

    def connect(self,
                protocol: str,
                host: str,
                req_port: int,
                sub_port: int
    ):
        addr_prefix = protocol + '://' + host + ':%s'

        req_addr = addr_prefix % req_port
        self._req_socket.connect(req_addr)
        self._logger.info('Ready to send commands on (REQ) socket: %s', req_addr)

        sub_addr = addr_prefix % sub_port
        self._sub_socket.connect(sub_addr)
        self._logger.info('Ready to receive quotes on (SUB) socket: %s', sub_addr)

    def disconnect(self):
        self._req_socket.close()
        self._sub_socket.close()

    @property
    def account(self) -> Account:
        if self._account is None:
            self._account = self._get_account()

        return self._account

    def get_tick(self, symbol: str) -> Tick:
        request  = requests.GetTickRequest(symbol)
        response = responses.GetTickResponse(self._send_request(request))
        
        return response.tick()

    def get_instrument(self, symbol: str) -> Instrument:
        if symbol not in self._instruments:
            request  = requests.GetInstrumentRequest(symbol)
            response = responses.GetInstrumentResponse(self._send_request(request))

            instrument = Instrument(
                symbol          = symbol,
                description     = response.description(),
                base_currency   = response.base_currency(),
                profit_currency = response.profit_currency(),
                margin_currency = response.margin_currency(),
                decimal_places  = response.decimal_places(),
                point           = response.point(),
                tick_size       = response.tick_size(),
                contract_size   = response.contract_size(),
                lot_step        = response.lot_step(),
                min_lot         = response.min_lot(),
                max_lot         = response.max_lot(),
                min_stop_level  = response.min_stop_level(),
                freeze_level    = response.freeze_level(),
                spread          = response.spread()
            )

            self._instruments[symbol] = instrument

        return self._instruments[symbol]
    
    def get_history_bars(self,
                         symbol: str,
                         start_time: Optional[datetime] = None,
                         end_time:   Optional[datetime] = None,
                         timeframe:  Timeframe = Timeframe.M1
    ) -> List[Bar]:
        request  = requests.GetHistoryBarsRequest(symbol, start_time, end_time, timeframe)
        response = responses.GetHistoryBarsResponse(self._send_request(request))
        
        return response.bars()

    def get_bar(self,
                symbol: str,
                index: int = 0,
                timeframe: Timeframe = Timeframe.M1
    ) -> Bar:
        request  = requests.GetBarRequest(symbol, index, timeframe)
        response = responses.GetBarResponse(self._send_request(request))

        return response.bar()

    def subscribe(self, symbol: str):
        if symbol in self._subscribed_symbols:
            return

        request = requests.WatchSymbolRequest(symbol)

        try:
            self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.UNKNOWN_SYMBOL:
                raise rmt.error.InvalidSymbol(symbol)
            else:
                raise e

        self._sub_socket.subscribe('tick.' + symbol)
        self._subscribed_symbols.add(symbol)

    def subscribe_all(self):
        request  = requests.WatchSymbolRequest('*')
        response = responses.WatchSymbolResponse(self._send_request(request))
        
        for symbol in response.symbols():
            if isinstance(symbol, str):
                self._sub_socket.subscribe('tick.' + symbol)
                self._subscribed_symbols.add(symbol)

    def unsubscribe(self, symbol: str):
        if symbol in self._subscribed_symbols:
            self._sub_socket.unsubscribe('tick.' + symbol)
            self._subscribed_symbols.remove(symbol)

    def unsubscribe_all(self):
        for symbol in self._subscribed_symbols:
            self._sub_socket.unsubscribe('tick' + symbol)
        
        self._subscribed_symbols.clear()

    def subscriptions(self) -> Set[str]:
        return self._subscribed_symbols.copy()

    def place_order(self,
                    symbol:       str,
                    side:         Side,
                    order_type:   OrderType,
                    lots:         float,
                    price:        Optional[float] = None,
                    slippage:     Optional[int]   = None,
                    stop_loss:    Optional[float] = None,
                    take_profit:  Optional[float] = None,
                    comment:      str = '',
                    magic_number: int = 0,
                    expiration:   Optional[datetime] = None
    ) -> int:
        if symbol == '':
            raise ValueError('instrument symbol must not be empty')

        side       = Side(side)
        order_type = OrderType(order_type)
        opcode     = None

        if order_type == OrderType.MARKET_ORDER:
            opcode = OperationCode.BUY if side == Side.BUY else OperationCode.SELL

        elif order_type == OrderType.LIMIT_ORDER:
            opcode = OperationCode.BUY_LIMIT if side == Side.BUY else OperationCode.SELL_LIMIT

        else:
            opcode = OperationCode.BUY_STOP if side == Side.BUY else OperationCode.SELL_STOP

        request = requests.PlaceOrderRequest(
            symbol,
            opcode,
            lots,
            price,
            slippage,
            stop_loss,
            take_profit,
            comment,
            magic_number,
            expiration
        )

        response_content = None

        try:
            response_content = self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.UNKNOWN_SYMBOL:
                raise rmt.error.InvalidSymbol(symbol)

            elif e.code == CommandResultCode.OFF_QUOTES:
                raise rmt.error.OffQuotes(symbol, side, order_type)

            elif e.code == CommandResultCode.REQUOTE:
                raise rmt.error.Requote(symbol, price)

            else:
                raise e

        response = responses.PlaceOrderResponse(response_content)

        order_info = response.order_info()
        order = None

        ################################################################################
        # Add order to list of tracked orders if the response also contains information
        # about the order.
        # 
        # This accounts for the case a call to OrderSend() succeeds, but a subsequent
        # call to OrderSelect() fails. If the call to OrderSelect() succeeded, then all
        # the remaining information about the order MUST be present in the response.
        # We then store the order in the list of tracked orders, since we will have ALL
        # information about the order. Note that redundant information that we already
        # have (such as symbol, side, etc.) is not sent in the response.
        #
        # OTOH, if OrderSelect() fails, then we simply ignore it and return the order's
        # ticket, since an order was successfully placed. In this case, if get_order()
        # is called immediately after this method returns, we will attempt to retrieve
        # info about the order again from the server. In that case, if OrderSelect()
        # fails another time, *then* an exception is raised.
        ################################################################################
        if order_info is not None:
            status = None

            if order_type == OrderType.MARKET_ORDER:
                if order_info.lots() < lots:
                    status = OrderStatus.PARTIALLY_FILLED
                else:
                    status = OrderStatus.FILLED
            else:
                status = OrderStatus.PENDING

            order = Order(
                symbol       = symbol,
                side         = side,
                type         = order_type,
                lots         = order_info.lots(),
                status       = status,
                open_price   = order_info.open_price(),
                open_time    = order_info.open_time(),
                close_price  = None,
                close_time   = None,
                expiration   = expiration,
                stop_loss    = stop_loss,
                take_profit  = take_profit,
                magic_number = int(magic_number),
                comment      = str(comment),
                commission   = order_info.commission(),
                profit       = order_info.profit(),
                swap         = order_info.swap(),
            )

        ticket = response.ticket()

        self._orders[ticket] = order

        return ticket

    def modify_order(self,
                     ticket:      int,
                     stop_loss:   Optional[float]    = None,
                     take_profit: Optional[float]    = None,
                     price:       Optional[float]    = None,
                     expiration:  Optional[datetime] = None
    ):
        # Ensure at least one parameter is not None.
        if all(value is None for value in [stop_loss, take_profit, price, expiration]):
            return

        request = requests.ModifyOrderRequest(
            ticket,
            stop_loss,
            take_profit,
            price,
            expiration
        )

        try:
            self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.INVALID_TICKET:
                raise rmt.error.InvalidTicket(ticket)
            else:
                raise e

        try:
            order = self._orders[ticket]

            if order is None:
                return
            
            if stop_loss is not None:
                order._stop_loss = float(stop_loss)

            if take_profit is not None:
                order._take_profit = float(take_profit)

            if price is not None:
                order._open_price = float(price)

            if expiration is not None:
                order._expiration = expiration

        except KeyError:
            pass

    def cancel_order(self, ticket: int):
        request = requests.CancelOrderRequest(ticket)

        try:
            self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.INVALID_TICKET:
                raise rmt.error.InvalidTicket(ticket)
            else:
                raise e

        try:
            order = self._orders[ticket]

            if order is not None:
                order._status = OrderStatus.CANCELED

        except KeyError:
            pass

    def close_order(self,
                    ticket:   int,
                    price:    Optional[float] = None,
                    slippage: int             = 0,
                    lots:     Optional[float] = None
    ) -> int:
        request = requests.CloseOrderRequest(ticket, price, slippage, lots)
        response_content = None

        try:
            response_content = self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.INVALID_TICKET:
                raise rmt.error.InvalidTicket(ticket)
            else:
                raise e

        response = responses.CloseOrderResponse(response_content)

        try:
            order = self._orders[ticket]

            if order is not None:
                order._status      = OrderStatus.CLOSED
                order._lots        = response.lots()
                order._close_price = response.close_price()
                order._close_time  = response.close_time()
                order._comment     = response.comment()
                order._commission  = response.commission()
                order._profit      = response.profit()
                order._swap        = response.swap()
        
        except KeyError:
            pass

        new_order = response.new_order()

        if new_order is not None:
            ticket = new_order.ticket()

            order = Order(
                symbol       = order.symbol(),
                side         = order.side(),
                type         = order.type(),
                lots         = new_order.lots(),
                status       = OrderStatus.FILLED,
                open_price   = order.open_price(),
                open_time    = order.open_time(),
                stop_loss    = order.stop_loss(),
                take_profit  = order.take_profit(),
                magic_number = new_order.magic_number(),
                comment      = new_order.comment(),
                commission   = new_order.commission(),
                profit       = new_order.profit(),
                swap         = new_order.swap()
            )

            self._orders[ticket] = order

        return ticket

    def get_order(self, ticket: int) -> Order:
        try:
            order = self._orders[ticket]

            if order is not None:
                return order

        except KeyError:
            pass

        request = requests.GetOrderRequest(ticket)
        response_content = None

        try:
            response_content = self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.INVALID_TICKET:
                raise rmt.error.InvalidTicket(ticket)
            else:
                raise e

        response = responses.GetOrderResponse(response_content)

        self._orders[ticket] = response.order()

        return response.order()

    def get_exchange_rate(self, base_currency: str, quote_currency: str) -> float:
        request = requests.GetExchangeRateRequest(base_currency, quote_currency)

        try:
            response = responses.GetExchangeRateResponse(self._send_request(request))
            return response.rate()
        except MQL4Error as e:
            if e.code == CommandResultCode.EXCHANGE_RATE_FAILED:
                raise rmt.error.ExchangeRateError(base_currency, quote_currency)
            else:
                raise e

    def process_events(self):
        while True:
            try:
                event_msg = self._sub_socket.recv_string(zmq.DONTWAIT)
                
                self._logger.debug('received event message: %s', event_msg)
                self._process_event(event_msg)

            except zmq.error.Again:
                break
            except (ValueError, TypeError) as e:
                self._logger.warning('failed to read event msg: %s', e)

    #===============================================================================
    # Internals (U Can't Touch This)
    #===============================================================================
    def _get_account(self) -> Account:
        request  = requests.GetAccountRequest()
        response = responses.GetAccountResponse(self._send_request(request))

        return response.account()

    def _parse_response(self, response: str) -> Tuple[CommandResultCode, Optional[Content]]:
        sep_index  = response.find(' ')
        cmd_result = None

        if sep_index == -1:
            cmd_result = response
        else:
            cmd_result = response[0:sep_index]

        cmd_result = int(cmd_result)
        content    = None

        if sep_index != -1:
            content = response[(sep_index + 1):]
            content = json.loads(content)

            if not isinstance(content, (dict, list)):
                raise ValueError(
                    'response content is not valid JSON (expected object or array, got: %s)'
                    % type(content)
                )
        
        return CommandResultCode(cmd_result), content

    def _send_request(self, request: requests.Request) -> Content:
        cmd = request.command

        if cmd == '':
            raise rmt.error.RequestError("empty attribute 'command' of request object %s" % type(request))
        
        if not cmd.isalpha():
            raise rmt.error.RequestError("expected alphabetic command string (got: '%s')" % request.command)

        try:
            content      = json.dumps(request.content())
            request: str = '%s %s' % (cmd, content)            
        except (rmt.error.NotImplementedException, ValueError) as e:
            raise rmt.error.RequestError('failed to serialize JSON request: %s' % e)

        response: str = ''

        try:
            self._req_socket.send_string(request)
            self._logger.debug('sent request: %s', request)

            response = self._req_socket.recv_string()
            self._logger.debug('received response: %s', response)

        except zmq.error.Again:
            sleep(0.000000001)
            raise rmt.error.RequestTimeout()

        cmd_result = None
        content    = None

        try:
            cmd_result, content = self._parse_response(response)
        except ValueError as e:
            raise rmt.error.RequestError('parsing of response message failed: %s' % e)

        if content is None:
            content = {}

        if cmd_result != CommandResultCode.SUCCESS:
            raise_error(cmd, cmd_result, content)

        return content

    def _process_event(self, msg: str):
        """Parses, validates, and notifies an event message.

        Raises
        ------
        ValueError
            If message name is unknown or message body is invalid.
        
        TypeError
            If message body is of an invalid type or has a required value of an invalid type.
        """

        content_index = msg.find(' ')
        
        if content_index == -1:
            raise ValueError("missing content from event message '%s'" % msg)
        
        content = None

        try:
            content = msg[(content_index + 1):]
        except:
            raise ValueError("missing content from event message '%s'" % msg)

        content    = json.loads(content)
        event_name = msg[:content_index]

        if not isinstance(content, (dict, list)):
            raise ValueError("content of event message '%s' is not valid JSON", event_name)

        self._event_dispatcher.dispatch(event_name, content)

    def _on_tick_event(self, event: events.TickEvent):
        self.tick_received.emit(event.symbol(), event.tick())

    def _on_order_placed_event(self, event: events.OrderPlacedEvent):
        ticket      = event.ticket()
        event_order = event.order()

        tracked_order = None

        try:
            tracked_order = self._orders[ticket]
        except KeyError:
            pass

        if tracked_order is None:
            self._orders[ticket] = event_order
        else:
            tracked_order._side         = event_order.side()
            tracked_order._type         = event_order.type()
            tracked_order._lots         = event_order.lots()
            tracked_order._status       = event_order.status()
            tracked_order._open_price   = event_order.open_price()
            tracked_order._open_time    = event_order.open_time()
            tracked_order._stop_loss    = event_order.stop_loss()
            tracked_order._take_profit  = event_order.take_profit()
            tracked_order._expiration   = event_order.expiration()
            tracked_order._magic_number = event_order.magic_number()
            tracked_order._comment      = event_order.comment()
            tracked_order._commission   = event_order.commission()
            tracked_order._profit       = event_order.profit()
            tracked_order._swap         = event_order.swap()
        
        if event_order.status() == OrderStatus.PENDING:
            self.order_opened.emit(ticket)
        else:
            self.order_filled.emit(ticket)
    
    def _on_order_finished_event(self, event: events.OrderFinishedEvent):
        ticket = event.ticket()
        order = None

        try:
            order = self._orders[ticket]
        except KeyError:
            return

        if order is not None:
            order._status      = event.status()
            order._close_price = event.close_price()
            order._close_time  = event.close_time()
            order._stop_loss   = event.stop_loss()
            order._take_profit = event.take_profit()
            order._expiration  = event.expiration()
            order._comment     = event.comment()
            order._commission  = event.commission()
            order._profit      = event.profit()
            order._swap        = event.swap()

        if event.status() == OrderStatus.CLOSED:
            self.order_closed.emit(ticket)

        elif event.status() == OrderStatus.CANCELED:
            self.order_canceled.emit(ticket)

        else:
            self.order_expired.emit(ticket)

    def _on_order_modified_event(self, event: events.OrderModifiedEvent):
        ticket = event.ticket()
        order = None

        try:
            order = self._orders[ticket]
        except KeyError:
            return

        if order is not None:
            order._open_price  = event.open_price()
            order._stop_loss   = event.stop_loss()
            order._take_profit = event.take_profit()
            order._expiration  = event.expiration()

        self.order_modified.emit(ticket)

    def _on_order_updated_event(self, event: events.OrderUpdatedEvent):
        ticket = event.ticket()
        order = None

        try:
            order = self._orders[ticket]
        except KeyError:
            return

        if order is not None:
            order._comment    = event.comment()
            order._commission = event.commission()
            order._profit     = event.profit()
            order._swap       = event.swap()

        self.order_updated.emit(ticket)
import zmq
import json
import logging
from datetime import datetime
from typing   import Dict, List, Optional, Set, Tuple
from time     import sleep
from rmt      import (error, Order, Side, OrderType,
                      Exchange, Tick, Bar, OrderStatus,
                      Timeframe)
from . import mt4

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

        self._subscribed_symbols: Set[str] = set()
        self._logger = logging.getLogger(MetaTrader4.__name__)

        self._orders: Dict[int, Order] = {}

        self._event_factory = {
            'tick': (mt4.events.TickEvent, lambda e: self.tick_received.emit(e.symbol(), e.tick()))
        }

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
        self._logger.info('Ready to receive quotes on (PULL) socket: %s', sub_addr)

    def disconnect(self):
        self._req_socket.close()
        self._sub_socket.close()

    def get_tick(self, symbol: str) -> Tick:
        request  = mt4.requests.GetTickRequest(symbol)
        response = mt4.responses.GetTickResponse(self._send_request(request))
        
        return response.tick()

    def get_history_bars(self,
                         symbol: str,
                         start_time: Optional[datetime] = None,
                         end_time:   Optional[datetime] = None,
                         timeframe:  Timeframe = Timeframe.M1
    ) -> List[Bar]:
        request  = mt4.requests.GetHistoryBarsRequest(symbol, start_time, end_time, timeframe)
        response = mt4.responses.GetHistoryBarsResponse(self._send_request(request))
        
        return response.bars()

    def get_current_bar(self,
                        symbol:    str,
                        timeframe: Timeframe = Timeframe.M1
    ) -> Bar:
        request  = mt4.requests.GetCurrentBarRequest(symbol, timeframe)
        response = mt4.responses.GetCurrentBarResponse(self._send_request(request))

        return response.bar()

    def subscribe(self, symbol: str):
        if symbol in self._subscribed_symbols:
            return

        request = mt4.requests.WatchSymbolRequest(symbol)
        self._send_request(request)

        self._sub_socket.subscribe('tick.' + symbol)
        self._subscribed_symbols.add(symbol)

    def subscribe_all(self):
        request  = mt4.requests.WatchSymbolRequest('*')
        response = mt4.responses.WatchSymbolResponse(self._send_request(request))
        
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

        if side not in [Side.BUY, Side.SELL]:
            raise ValueError(
                "invalid value %s for type '%s'"
                % (side, type(Side))
            )

        opcode = None

        if order_type == OrderType.MARKET_ORDER:
            opcode = mt4.OperationCode.BUY if side == Side.BUY else mt4.OperationCode.SELL

        elif order_type == OrderType.LIMIT_ORDER:
            opcode = mt4.OperationCode.BUY_LIMIT if side == Side.BUY else mt4.OperationCode.SELL_LIMIT

        elif order_type == OrderType.STOP_ORDER:
            opcode = mt4.OperationCode.BUY_STOP if side == Side.BUY else mt4.OperationCode.SELL_STOP

        else:
            raise ValueError(
                "invalid value %s for type '%s'"
                % (order_type, type(OrderType))
            )

        request = mt4.requests.PlaceOrderRequest(
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

        response = mt4.responses.PlaceOrderResponse(self._send_request(request))

        order_info = response.order_info()

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

            self._orders[response.ticket()] = order

        return response.ticket()

    def modify_order(self,
                     ticket:      int,
                     stop_loss:   Optional[float]    = None,
                     take_profit: Optional[float]    = None,
                     price:       Optional[float]    = None,
                     expiration:  Optional[datetime] = None
    ):
        request = mt4.requests.ModifyOrderRequest(
            ticket,
            stop_loss,
            take_profit,
            price,
            expiration
        )

        self._send_request(request)

        # order._stop_loss   = float(stop_loss)
        # order._take_profit = float(take_profit)

        # if price is not None:
        #     order._open_price = float(price)

        # if expiration is not None:
        #     order._expiration = expiration

    def close_order(self,
                    ticket:   int,
                    price:    Optional[float] = None,
                    slippage: int             = 0,
                    lots:     Optional[float] = None
    ) -> int:
        request  = mt4.requests.CloseOrderRequest(ticket, price, slippage, lots)
        response = mt4.responses.CloseOrderResponse(self._send_request(request))

        # order._status      = OrderStatus.CLOSED
        # order._lots        = response.lots()
        # order._close_price = response.close_price()
        # order._close_time  = response.close_time()
        # order._comment     = response.comment()
        # order._commission  = response.commission()
        # order._profit      = response.profit()
        # order._swap        = response.swap()

        if response.new_order():
            ticket = response.new_order().ticket()

        #     order = Order(
        #         ticket       = response.new_order_ticket(),
        #         symbol       = order.symbol(),
        #         side         = order.side(),
        #         type         = order.type(),
        #         lots         = response.new_order_lots(),
        #         status       = OrderStatus.FILLED,
        #         open_price   = order.open_price(),
        #         open_time    = order.open_time(),
        #         stop_loss    = order.stop_loss(),
        #         take_profit  = order.take_profit(),
        #         magic_number = response.new_order_magic_number(),
        #         comment      = response.new_order_comment(),
        #         commission   = response.new_order_commission(),
        #         profit       = response.new_order_profit(),
        #         swap         = response.new_order_swap()
        #     )

        return ticket

    def get_order(self, ticket: int) -> Order:
        if ticket not in self._orders:
            # TODO: implement 'getOrder' command
            pass

        return self._orders[ticket]

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
    def _parse_response(self, response: str) -> Tuple[mt4.CommandResultCode, Optional[mt4.Content]]:
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
        
        return mt4.CommandResultCode(cmd_result), content

    def _send_request(self, request: mt4.requests.Request) -> mt4.Content:
        cmd = request.command

        if cmd == '':
            raise error.RequestError("empty attribute 'command' of request object %s" % type(request))
        
        if not cmd.isalpha():
            raise error.RequestError("expected alphabetic command string (got: '%s')" % request.command)

        try:
            content      = json.dumps(request.content())
            request: str = '%s %s' % (cmd, content)            
        except (NotImplementedError, ValueError) as e:
            raise error.RequestError('failed to serialize JSON request: %s' % e)

        response: str = ''

        try:
            self._req_socket.send_string(request)
            self._logger.debug('sent request: %s', request)

            response = self._req_socket.recv_string()
            self._logger.debug('received response: %s', response)

        except zmq.error.Again:
            sleep(0.000000001)
            raise error.RequestTimeout()

        cmd_result = None
        content    = None

        try:
            cmd_result, content = self._parse_response(response)
        except ValueError as e:
            raise error.RequestError('parsing of response message failed: %s' % e)

        if content is None:
            content = {}

        if cmd_result != mt4.CommandResultCode.SUCCESS:
            mt4.raise_error(cmd, cmd_result, content)

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

        static_name = None
        dynamic_name = None
        dynamic_name_index = event_name.find('.')

        if dynamic_name_index != -1:
            static_name  = event_name[0:dynamic_name_index]
            dynamic_name = event_name[(dynamic_name_index + 1):]
        else:
            static_name = event_name

        if not static_name.isalpha():
            raise ValueError("expected alphabetic static part of event name (got: '%s')" % static_name)

        if static_name not in self._event_factory:
            raise ValueError("received event message with unknown name '%s'" % static_name)

        event_data    = self._event_factory[static_name]
        EventType     = event_data[0]
        event_emitter = event_data[1]
        event_obj     = None

        if dynamic_name is not None:
            event_obj = EventType(dynamic_name, content)
        else:
            event_obj = EventType(static_name, content)

        event_emitter(event_obj)

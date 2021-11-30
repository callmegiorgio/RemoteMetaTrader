import zmq
import json
import logging
import rmt
import pytz
from datetime import datetime, tzinfo
from typing   import Dict, List, Optional, Set, Tuple
from time     import sleep
from rmt      import (
    Order, Side, OrderType, Exchange, Tick,
    Bar, OrderStatus, Timeframe, Instrument,
    Account, TradeMode, MarginMode
)
from . import *

class MetaTrader4(Exchange):
    """Bindings for executing market operations on MetaTrader 4."""

    def __init__(self,
                 protocol: str = 'tcp',
                 host:     str = 'localhost',
                 req_port: int = 32768,
                 sub_port: int = 32769,
                 timezone: pytz.BaseTzInfo = pytz.utc
    ):
        super().__init__(timezone)

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
        self._sub_socket.subscribe('accountChanged')
        self._sub_socket.subscribe('equityUpdated')

        self._event_dispatcher = events.Dispatcher()
        self._event_dispatcher.register('tick',           events.TickEvent,           self._on_tick_event)
        self._event_dispatcher.register('bar',            events.BarClosedEvent,      self._on_bar_closed_event)
        self._event_dispatcher.register('orderPlaced',    events.OrderPlacedEvent,    self._on_order_placed_event)
        self._event_dispatcher.register('orderFinished',  events.OrderFinishedEvent,  self._on_order_finished_event)
        self._event_dispatcher.register('orderModified',  events.OrderModifiedEvent,  self._on_order_modified_event)
        self._event_dispatcher.register('orderUpdated',   events.OrderUpdatedEvent,   self._on_order_updated_event)
        self._event_dispatcher.register('accountChanged', events.AccountChangedEvent, self._on_account_changed_event)
        self._event_dispatcher.register('equityUpdated',  events.EquityUpdatedEvent,  self._on_equity_updated_event)

        self._subscribed_symbols: Set[str] = set()
        self._logger = logging.getLogger(MetaTrader4.__name__)

        self._account: Optional[Account] = None

        self._instruments: Dict[str, Instrument] = {}
        self._orders:      Dict[int, Order] = {}

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
        request  = requests.GetTick(symbol)
        response = responses.GetTick(self._send_request(request))

        tick = Tick(
            time = self._utc_from_string(response.time()),
            bid  = response.bid(),
            ask  = response.ask()
        )

        return tick

    def get_instrument(self, symbol: str) -> Instrument:
        if symbol not in self._instruments:
            request  = requests.GetInstrument(symbol)
            response = responses.GetInstrument(self._send_request(request))

            instrument = Instrument(
                symbol          = symbol,
                description     = response.description(),
                base_currency   = response.base_currency(),
                quote_currency  = response.quote_currency(),
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
    
    def get_instruments(self) -> List[Instrument]:
        request  = requests.GetInstruments()
        response = responses.GetInstruments(self._send_request(request))

        instrument_count = response.instrument_count()

        for i in range(instrument_count):
            symbol = response.symbol(i)

            instrument = Instrument(
                symbol          = symbol,
                description     = response.description(i),
                base_currency   = response.base_currency(i),
                quote_currency  = response.quote_currency(i),
                margin_currency = response.margin_currency(i),
                decimal_places  = response.decimal_places(i),
                point           = response.point(i),
                tick_size       = response.tick_size(i),
                contract_size   = response.contract_size(i),
                lot_step        = response.lot_step(i),
                min_lot         = response.min_lot(i),
                max_lot         = response.max_lot(i),
                min_stop_level  = response.min_stop_level(i),
                freeze_level    = response.freeze_level(i),
                spread          = response.spread(i)
            )

            self._instruments[symbol] = instrument

        return self._instruments.copy().values()

    def get_history_bars(self,
                         symbol: str,
                         start_time: Optional[datetime] = None,
                         end_time:   Optional[datetime] = None,
                         timeframe:  Timeframe = Timeframe.M1
    ) -> List[Bar]:
        start_time = None if start_time is None else self._datetime_to_string(start_time)
        end_time   = None if end_time   is None else self._datetime_to_string(end_time)

        request  = requests.GetHistoryBars(symbol, start_time, end_time, timeframe)
        response = responses.GetHistoryBars(self._send_request(request))

        bar_count = response.bar_count()
        bars = []

        for i in range(bar_count):
            bar = Bar(
                time   = self._utc_from_string(response.time(i)),
                open   = response.open(i),
                high   = response.high(i),
                low    = response.low(i),
                close  = response.close(i),
                volume = response.volume(i)
            )

            bars.append(bar)
        
        return bars

    def get_bar(self,
                symbol: str,
                index: int = 0,
                timeframe: Timeframe = Timeframe.M1
    ) -> Bar:
        request  = requests.GetBar(symbol, index, timeframe)
        response = responses.GetBar(self._send_request(request))

        bar = Bar(
            time   = self._utc_from_string(response.time()),
            open   = response.open(),
            high   = response.high(),
            low    = response.low(),
            close  = response.close(),
            volume = response.volume()
        )

        return bar

    def subscribe(self, symbol: str):
        if symbol in self._subscribed_symbols:
            return

        request = requests.WatchSymbol(symbol)

        try:
            self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.UNKNOWN_SYMBOL:
                raise rmt.error.InvalidSymbol(symbol) from None
            else:
                raise e from None

        self._subscribe_instrument_event(symbol)
        self._subscribed_symbols.add(symbol)

    def subscribe_all(self):
        request  = requests.WatchSymbolRequest('*')
        response = responses.WatchSymbolResponse(self._send_request(request))
        
        for symbol in response.symbols():
            if isinstance(symbol, str):
                self._subscribe_instrument_event(symbol)
                self._subscribed_symbols.add(symbol)

    def unsubscribe(self, symbol: str):
        if symbol in self._subscribed_symbols:
            self._unsubscribe_instrument_event(symbol)
            self._subscribed_symbols.remove(symbol)

    def unsubscribe_all(self):
        for symbol in self._subscribed_symbols:
            self._unsubscribe_instrument_event(symbol)
        
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
    ) -> Order:
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

        request = requests.PlaceOrder(
            symbol,
            opcode,
            lots,
            price,
            slippage,
            stop_loss,
            take_profit,
            comment,
            magic_number,
            None if expiration is None else expiration.astimezone(self.timezone)
        )

        response_content = None

        try:
            response_content = self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.UNKNOWN_SYMBOL:
                raise rmt.error.InvalidSymbol(symbol) from None

            elif e.code == CommandResultCode.OFF_QUOTES:
                raise rmt.error.OffQuotes(symbol, side, order_type) from None

            elif e.code == CommandResultCode.REQUOTE:
                raise rmt.error.Requote(symbol) from None

            elif e.code == CommandResultCode.INVALID_STOPS:
                raise rmt.error.InvalidStops(stop_loss, take_profit)

            else:
                raise e from None

        response = responses.PlaceOrder(response_content)

        response_ticket     = response.ticket()
        response_lots       = response.lots()
        response_open_price = response.open_price()
        response_open_time  = response.open_time()
        response_commission = response.commission()
        response_profit     = response.profit()
        response_swap       = response.swap()

        if order_type == OrderType.MARKET_ORDER:
            if response_lots < lots:
                status = OrderStatus.PARTIALLY_FILLED
            else:
                status = OrderStatus.FILLED
        else:
            status = OrderStatus.PENDING

        order = Order(
            ticket       = response_ticket,
            symbol       = symbol,
            side         = side,
            type         = order_type,
            lots         = response_lots,
            status       = status,
            open_price   = response_open_price,
            open_time    = None if response_open_time is None else self._utc_from_string(response_open_time),
            expiration   = expiration,
            stop_loss    = stop_loss,
            take_profit  = take_profit,
            magic_number = int(magic_number),
            comment      = str(comment),
            commission   = response_commission,
            profit       = response_profit,
            swap         = response_swap
        )

        self._orders[response_ticket] = order

        return order

    def modify_order(self,
                     order:       Order,
                     stop_loss:   Optional[float]    = None,
                     take_profit: Optional[float]    = None,
                     price:       Optional[float]    = None,
                     expiration:  Optional[datetime] = None
    ):
        request = requests.ModifyOrder(
            order.ticket,
            stop_loss,
            take_profit,
            price,
            None if expiration is None else expiration.astimezone(self.timezone)
        )

        try:
            self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.INVALID_TICKET:
                raise rmt.error.InvalidTicket(order.ticket) from None
            else:
                raise e from None

        order._stop_loss   = None if stop_loss   is None else float(stop_loss)
        order._take_profit = None if take_profit is None else float(take_profit)

        if order.type != OrderType.MARKET_ORDER:
            if price is not None:
                order._open_price = float(price)

            if expiration is not None:
                order._expiration = expiration

    def cancel_order(self, order: Order):
        request = requests.CancelOrder(order.ticket)

        try:
            self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.INVALID_TICKET:
                raise rmt.error.InvalidTicket(order.ticket) from None
            else:
                raise e from None

        order._status = OrderStatus.CANCELED

    def close_order(self,
                    order:    Order,
                    price:    Optional[float] = None,
                    slippage: int             = 0,
                    lots:     Optional[float] = None
    ) -> Optional[Order]:
        request = requests.CloseOrder(order.ticket, price, slippage, lots)
        response_content = None

        try:
            response_content = self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.INVALID_TICKET:
                raise rmt.error.InvalidTicket(order.ticket) from None
            else:
                raise e from None

        response = responses.CloseOrder(response_content)

        order._status      = OrderStatus.CLOSED
        order._lots        = response.lots()
        order._close_price = response.close_price()
        order._close_time  = self._utc_from_string(response.close_time())
        order._comment     = response.comment()
        order._commission  = response.commission()
        order._profit      = response.profit()
        order._swap        = response.swap()

        new_order = response.new_order()

        if new_order is not None:
            ticket = new_order.ticket()

            new_order = Order(
                ticket       = ticket,
                symbol       = order.symbol,
                side         = order.side,
                type         = order.type,
                lots         = new_order.lots(),
                status       = OrderStatus.FILLED,
                open_price   = order.open_price,
                open_time    = order.open_time,
                stop_loss    = order.stop_loss,
                take_profit  = order.take_profit,
                magic_number = new_order.magic_number(),
                comment      = new_order.comment(),
                commission   = new_order.commission(),
                profit       = new_order.profit(),
                swap         = new_order.swap()
            )

            self._orders[ticket] = new_order

        return new_order

    def get_order(self, ticket: int) -> Order:
        try:
            return self._orders[ticket]
        except KeyError:
            pass

        request = requests.GetOrder(ticket)
        response_content = None

        try:
            response_content = self._send_request(request)
        except MQL4Error as e:
            if e.code == CommandResultCode.INVALID_TICKET:
                raise rmt.error.InvalidTicket(ticket) from None
            else:
                raise e from None

        response = responses.GetOrder(response_content)

        opcode = OperationCode(response.opcode())
        status = response.status()
        
        if   status == 'pending':  status = OrderStatus.PENDING
        elif status == 'filled':   status = OrderStatus.FILLED
        elif status == 'canceled': status = OrderStatus.CANCELED
        elif status == 'expired':  status = OrderStatus.EXPIRED
        elif status == 'closed':   status = OrderStatus.CLOSED
        else:
            raise ValueError("invalid order status '{}'".format(status))

        side       = None
        order_type = None

        if opcode in [OperationCode.BUY, OperationCode.SELL]:
            side       = Side.BUY if opcode == OperationCode.BUY else Side.SELL
            order_type = OrderType.MARKET_ORDER
        elif opcode in [OperationCode.BUY_LIMIT, OperationCode.SELL_LIMIT]:
            side       = Side.BUY if opcode == OperationCode.BUY_LIMIT else Side.SELL
            order_type = OrderType.LIMIT_ORDER
        else:
            side       = Side.BUY if opcode == OperationCode.BUY_STOP else Side.SELL
            order_type = OrderType.STOP_ORDER

        close_price = response.close_price()
        close_time  = response.close_time()

        if status == OrderStatus.CLOSED:
            if close_price is None:
                raise ValueError("missing close price in response of command get_order()")
            
            if close_time is None:
                raise ValueError("missing close time in response of command get_order()")

        open_time  = response.open_time()
        expiration = response.expiration()

        order = Order(
            ticket       = ticket,
            symbol       = response.symbol(),
            side         = side,
            type         = order_type,
            lots         = response.lots(),
            status       = status,
            open_price   = response.open_price(),
            open_time    = None if open_time is None else self._utc_from_string(open_time),
            close_price  = close_price,
            close_time   = None if close_time is None else self._utc_from_string(close_time),
            stop_loss    = response.stop_loss(),
            take_profit  = response.take_profit(),
            expiration   = None if expiration is None else self._utc_from_string(expiration),
            magic_number = response.magic_number(),
            comment      = response.comment(),
            commission   = response.commission(),
            profit       = response.profit(),
            swap         = response.swap()
        )

        self._orders[ticket] = order

        return order

    def get_exchange_rate(self, base_currency: str, quote_currency: str) -> float:
        request = requests.GetExchangeRate(base_currency, quote_currency)

        try:
            response = responses.GetExchangeRate(self._send_request(request))
            return response.rate()
        except MQL4Error as e:
            if e.code == CommandResultCode.EXCHANGE_RATE_FAILED:
                raise rmt.error.ExchangeRateError(base_currency, quote_currency) from None
            else:
                raise e from None

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
        request  = requests.GetAccount()
        response = responses.GetAccount(self._send_request(request))

        account = Account(
            login                 = response.login(),
            name                  = response.name(),
            server                = response.server(),
            company               = response.company(),
            trade_mode            = TradeMode(response.trade_mode()),
            margin_mode           = MarginMode(response.margin_mode()),
            leverage              = response.leverage(),
            order_limit           = response.order_limit(),
            currency              = response.currency(),
            balance               = response.balance(),
            credit                = response.credit(),
            profit                = response.profit(),
            equity                = response.equity(),
            margin                = response.margin(),
            free_margin           = response.free_margin(),
            margin_level          = response.margin_level(),
            margin_call_level     = response.margin_call_level(),
            margin_stop_out_level = response.margin_stop_out_level(),
            trade_allowed         = response.is_trade_allowed(),
            expert_allowed        = response.is_expert_allowed()
        )

        return account
    
    def _subscribe_instrument_event(self, symbol: str):
        self._sub_socket.subscribe('tick.' + symbol)
        self._sub_socket.subscribe('bar.' + symbol)

    def _unsubscribe_instrument_event(self, symbol: str):
        self._sub_socket.unsubscribe('tick.' + symbol)
        self._sub_socket.unsubscribe('bar.' + symbol)

    def _utc_from_string(self, dt_string: str) -> datetime:
        """Creates a UTC time from a datetime string which is in broker's timezone."""

        naive_dt     = datetime.strptime(dt_string, '%Y.%m.%d %H:%M:%S')
        broker_tz_dt = self.timezone.localize(naive_dt)
        utc_dt       = broker_tz_dt.astimezone(pytz.utc)

        return utc_dt

    def _datetime_to_string(self, dt: datetime) -> str:
        broker_tz_dt = dt.astimezone(self.timezone)
        dt_string    = broker_tz_dt.strftime('%Y.%m.%d %H:%M:%S')

        return dt_string

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
            raise rmt.error.RequestError('failed to serialize JSON request: %s' % e) from None

        response: str = ''

        try:
            self._req_socket.send_string(request)
            self._logger.debug('sent request: %s', request)

            response = self._req_socket.recv_string()
            self._logger.debug('received response: %s', response)

        except zmq.error.Again:
            sleep(0.000000001)
            raise rmt.error.RequestTimeout() from None

        cmd_result = None
        content    = None

        try:
            cmd_result, content = self._parse_response(response)
        except ValueError as e:
            raise rmt.error.RequestError('parsing of response message failed: %s' % e) from None

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
        except IndexError:
            raise ValueError("missing content from event message '%s'" % msg) from None

        content    = json.loads(content)
        event_name = msg[:content_index]

        if not isinstance(content, (dict, list)):
            raise ValueError("content of event message '%s' is not valid JSON", event_name)

        self._event_dispatcher.dispatch(event_name, content)

    def _on_tick_event(self, event: events.TickEvent):
        tick = Tick(
            time = self._utc_from_string(event.time()),
            bid  = event.bid(),
            ask  = event.ask()
        )

        self.tick_received.emit(event.symbol(), tick)

    def _on_bar_closed_event(self, event: events.BarClosedEvent):
        bar = Bar(
            time   = self._utc_from_string(event.time()),
            open   = event.open(),
            high   = event.high(),
            low    = event.low(),
            close  = event.close(),
            volume = event.volume()
        )

        self.bar_closed.emit(event.symbol(), bar)

    def _on_order_placed_event(self, event: events.OrderPlacedEvent):
        ticket = event.ticket()
        order  = None

        try:
            order = self._orders[ticket]
        except KeyError:
            pass
        
        opcode       = OperationCode(event.opcode())
        symbol       = event.symbol()
        lots         = event.lots()
        open_price   = event.open_price()
        open_time    = self._utc_from_string(event.open_time())
        stop_loss    = event.stop_loss()
        take_profit  = event.take_profit()
        expiration   = event.expiration()
        expiration   = None if expiration is None else self._utc_from_string(expiration)
        magic_number = event.magic_number()
        comment      = event.comment()
        commission   = event.commission()
        profit       = event.profit()
        swap         = event.swap()

        side       = None
        order_type = None
        status     = None

        if opcode in [OperationCode.BUY, OperationCode.SELL]:
            side       = Side.BUY if opcode == OperationCode.BUY else Side.SELL
            order_type = OrderType.MARKET_ORDER
            status     = OrderStatus.FILLED

        elif opcode in [OperationCode.BUY_LIMIT, OperationCode.SELL_LIMIT]:
            side       = Side.BUY if opcode == OperationCode.BUY_LIMIT else Side.SELL
            order_type = OrderType.LIMIT_ORDER
            status     = OrderStatus.PENDING

        else:
            side       = Side.BUY if opcode == OperationCode.BUY_STOP else Side.SELL
            order_type = OrderType.STOP_ORDER
            status     = OrderStatus.PENDING

        if order is None:
            order = Order(
                ticket       = ticket,
                symbol       = symbol,
                side         = side,
                type         = order_type,
                lots         = lots,
                status       = status,
                open_price   = open_price,
                open_time    = open_time,
                stop_loss    = stop_loss,
                take_profit  = take_profit,
                expiration   = expiration,
                magic_number = magic_number,
                comment      = comment,
                commission   = commission,
                profit       = profit,
                swap         = swap
            )

            self._orders[ticket] = order
        else:
            order._side         = side
            order._type         = order_type
            order._lots         = lots
            order._status       = status
            order._open_price   = open_price
            order._open_time    = open_time
            order._stop_loss    = stop_loss
            order._take_profit  = take_profit
            order._expiration   = expiration
            order._magic_number = magic_number
            order._comment      = comment
            order._commission   = commission
            order._profit       = profit
            order._swap         = swap

        if status == OrderStatus.PENDING:
            self.order_opened.emit(order)
        else:
            self.order_filled.emit(order)
    
    def _on_order_finished_event(self, event: events.OrderFinishedEvent):
        ticket = event.ticket()
        order  = None

        try:
            order = self._orders[ticket]
        except KeyError:
            return

        opcode      = OperationCode(event.opcode())
        close_price = event.close_price()
        close_time  = self._utc_from_string(event.close_time())
        stop_loss   = event.stop_loss()
        take_profit = event.take_profit()
        expiration  = event.expiration()
        expiration  = None if expiration is None else self._utc_from_string(expiration)
        comment     = event.comment()
        commission  = event.commission()
        profit      = event.profit()
        swap        = event.swap()
        status      = None

        if opcode in [OperationCode.BUY, OperationCode.SELL]:
            status = OrderStatus.CLOSED
        elif expiration is not None:
            if int(expiration.timestamp()) > 0 and close_time >= expiration:
                status = OrderStatus.EXPIRED
            else:
                status = OrderStatus.CANCELED

        order._status      = status
        order._close_price = close_price
        order._close_time  = close_time
        order._stop_loss   = stop_loss
        order._take_profit = take_profit
        order._expiration  = expiration
        order._comment     = comment
        order._commission  = commission
        order._profit      = profit
        order._swap        = swap

        if status == OrderStatus.CLOSED:
            self.order_closed.emit(order)
        elif status == OrderStatus.CANCELED:
            self.order_canceled.emit(order)
        else:
            self.order_expired.emit(order)

    def _on_order_modified_event(self, event: events.OrderModifiedEvent):
        ticket = event.ticket()

        try:
            order = self._orders[ticket]

            order._open_price  = event.open_price()
            order._stop_loss   = event.stop_loss()
            order._take_profit = event.take_profit()
            order._expiration  = self._utc_from_string(event.expiration())

            self.order_modified.emit(order)
        except KeyError:
            pass

    def _on_order_updated_event(self, event: events.OrderUpdatedEvent):
        ticket = event.ticket()

        try:
            order = self._orders[ticket]
            
            order._comment    = event.comment()
            order._commission = event.commission()
            order._profit     = event.profit()
            order._swap       = event.swap()

            self.order_updated.emit(order)
        except KeyError:
            pass

    def _on_account_changed_event(self, event: events.AccountChangedEvent):
        self.account._currency       = event.currency()
        self.account._leverage       = event.leverage()
        self.account._credit         = event.credit()
        self.account._expert_allowed = event.is_expert_allowed()
        self.account._trade_allowed  = event.is_trade_allowed()
        self.account._order_limit    = event.max_active_orders()

        self.account_updated.emit(self.account)

    def _on_equity_updated_event(self, event: events.EquityUpdatedEvent):
        self.account._equity       = event.equity()
        self.account._profit       = event.profit()
        self.account._margin       = event.margin()
        self.account._margin_level = event.margin_level()
        self.account._free_margin  = event.free_margin()

        balance = event.balance()

        if balance is not None:
            self.account._balance = balance

        self.account_updated.emit(self.account)
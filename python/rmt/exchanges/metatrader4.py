import zmq
import json
import logging
from enum     import IntEnum
from datetime import datetime, timedelta, timezone
from typing   import List, Optional, Set, Tuple
from time     import sleep
from rmt      import (jsonutil, error, Order, Side, OrderType,
                      Exchange, Tick, Bar, OrderStatus)

class OperationCode(IntEnum):
    BUY        = 0
    SELL       = 1
    BUY_LIMIT  = 2
    SELL_LIMIT = 3
    BUY_STOP   = 4
    SELL_STOP  = 5

class MetaTrader4(Exchange):
    """Bindings for executing market operations on MetaTrader 4."""

    def __init__(self,
                 protocol: str = 'tcp',
                 host: str = 'localhost',
                 req_port: int = 32768,
                 sub_port: int = 32769
    ):
        super().__init__()

        ctx = zmq.Context.instance()
        self._req_socket = ctx.socket(zmq.REQ)
        self._sub_socket = ctx.socket(zmq.SUB)
        self._sub_socket.subscribe('')

        self._subscribed_symbols: Set[str] = set()
        self._logger = logging.getLogger(MetaTrader4.__name__)

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
        request = {
            'cmd': 'get_tick',
            'msg': {
                'symbol': symbol
            }
        }

        response = self._send_request_and_get_response(request)

        server_time = jsonutil.read_required(response, 'server_time', int)
        bid         = jsonutil.read_required(response, 'bid',         float)
        ask         = jsonutil.read_required(response, 'ask',         float)

        tick = Tick(
            server_time = datetime.fromtimestamp(server_time, timezone.utc),
            bid = bid,
            ask = ask
        )

        return tick

    def get_bars(self,
                 symbol: str,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None
    ) -> List[Bar]:
        request = {
            'cmd': 'get_bars',
            'msg': {
                'symbol': symbol
            }
        }

        if isinstance(start_time, datetime):
            request['msg']['start_time'] = int(start_time.timestamp())
        
        if isinstance(end_time, datetime):
            request['msg']['end_time'] = int(end_time.timestamp())
        
        response = self._send_request_and_get_response(request)

        bars_array = jsonutil.read_required(response, 'bars', list)
        bars = []

        for bar_subarr in bars_array:
            t = jsonutil.read_required(bar_subarr, 0, int)
            o = jsonutil.read_required(bar_subarr, 1, float)
            h = jsonutil.read_required(bar_subarr, 2, float)
            l = jsonutil.read_required(bar_subarr, 3, float)
            c = jsonutil.read_required(bar_subarr, 4, float)

            bars.append(
                Bar(
                    time  = datetime.fromtimestamp(t, timezone.utc),
                    open  = o,
                    high  = h,
                    low   = l,
                    close = c
                )
            )
        
        return bars

    def subscribe(self, symbol: str):
        if symbol in self._subscribed_symbols:
            return

        request = {
            'cmd': 'watch_symbol',
            'msg': {
                'symbol': symbol
            }
        }

        self._send_request_and_get_response(request)
        self._sub_socket.subscribe('tick:' + symbol)
        self._subscribed_symbols.add(symbol)

    def subscribe_all(self):
        request = {
            'cmd': 'watch_symbol',
            'msg': {
                'symbol': '*'
            }
        }

        response = self._send_request_and_get_response(request)
        symbols = jsonutil.read_required_key(response, 'symbols', List)

        for symbol in symbols:
            if isinstance(symbol, str):
                self._sub_socket.subscribe('tick:' + symbol)
                self._subscribed_symbols.add(symbol)

    def unsubscribe(self, symbol: str):
        if symbol in self._subscribed_symbols:
            self._sub_socket.unsubscribe('tick:' + symbol)
            self._subscribed_symbols.remove(symbol)

    def unsubscribe_all(self):
        for symbol in self._subscribed_symbols:
            self._sub_socket.unsubscribe('tick' + symbol)
        
        self._subscribed_symbols.clear()

    def subscriptions(self) -> Set[str]:
        return self._subscribed_symbols.copy()

    def place_market_order(self,
                           symbol: str,
                           side: Side,
                           lots: float,
                           price: float,
                           slippage: int = 0,
                           stop_loss: float = 0,
                           take_profit: float = 0,
                           comment: str = '',
                           magic_number: int = 0
    ) -> Order:
        opcode = None

        if side == Side.BUY:
            opcode = OperationCode.BUY
        elif side == Side.SELL:
            opcode = OperationCode.SELL
        else:
            raise ValueError('invalid Side value %s' % side.value)

        order = self._place_order(
            symbol       = str(symbol),
            side         = side,
            opcode       = opcode,
            lots         = float(lots),
            price        = float(price),
            slippage     = int(slippage),
            stop_loss    = float(stop_loss),
            take_profit  = float(take_profit),
            comment      = str(comment),
            magic_number = int(magic_number),
            expiration   = None
        )

        return order

    def place_limit_order(self,
                          symbol: str,
                          side: Side,
                          lots: float,
                          price: float,
                          stop_loss: float = 0,
                          take_profit: float = 0,
                          comment: str = '',
                          magic_number: int = 0,
                          expiration: Optional[datetime] = None
    ) -> Order:
        opcode = None

        if side == Side.BUY:
            opcode = OperationCode.BUY_LIMIT
        elif side == Side.SELL:
            opcode = OperationCode.SELL_LIMIT
        else:
            raise ValueError('invalid Side value %s' % side.value)

        order = self._place_order(
            symbol       = str(symbol),
            side         = side,
            opcode       = opcode,
            lots         = float(lots),
            price        = float(price),
            slippage     = int(0),
            stop_loss    = float(stop_loss),
            take_profit  = float(take_profit),
            comment      = str(comment),
            magic_number = int(magic_number),
            expiration   = expiration
        )

        return order

    def place_stop_order(self,
                         symbol: str,
                         side: Side,
                         lots: float,
                         price: float,
                         stop_loss: float = 0,
                         take_profit: float = 0,
                         comment: str = '',
                         magic_number: int = 0,
                         expiration: Optional[datetime] = None
    ) -> Order:
        opcode = None

        if side == Side.BUY:
            opcode = OperationCode.BUY_STOP
        elif side == Side.SELL:
            opcode = OperationCode.SELL_STOP
        else:
            raise ValueError('invalid Side value %s' % side.value)

        order = self._place_order(
            symbol       = str(symbol),
            side         = side,
            opcode       = opcode,
            lots         = float(lots),
            price        = float(price),
            slippage     = int(0),
            stop_loss    = float(stop_loss),
            take_profit  = float(take_profit),
            comment      = str(comment),
            magic_number = int(magic_number),
            expiration   = expiration
        )

        return order
    
    def close_order(self,
                    order: Order,
                    price: float,
                    slippage: int,
                    lots: Optional[float] = None
    ) -> Optional[Order]:
        """
        Closes a market order.

        If `order` is closed or pending, does nothing.

        Otherwise, sends a command to MT4 to invoke `OrderClose(order.ticket(), lots, slippage, price)`.

        If `lots` is less than `order.lots()`, MT4 is instructed to perform a partial order close.
        If the partial order close succeeds, the remaining open order is returned by this method.
        Otherwise, this method returns `None`.

        This method is designed such that no exception is raised if `order` is effectively closed
        on the MT4 side, provided, of course, that no network error or similar event occurs.
        """

        if lots is None:
            lots = order.lots()

        request = {
            'cmd': 'close_order',
            'msg': {
                'ticket':   int(order.ticket()),
                'lots':     float(lots),
                'price':    float(price),
                'slippage': int(slippage)
            }
        }

        response = self._send_request_and_get_response(request)

        order._close_price = jsonutil.read_optional(response, 'cp',         float)
        close_utcts        = jsonutil.read_optional(response, 'ct',         int)
        order._lots        = jsonutil.read_optional(response, 'lots',       float)
        order._comment     = jsonutil.read_optional(response, 'comment',    str)
        order._commission  = jsonutil.read_optional(response, 'commission', float)
        order._profit      = jsonutil.read_optional(response, 'profit',     float)
        order._swap        = jsonutil.read_optional(response, 'swap',       float)

        order._close_time = datetime.fromtimestamp(close_utcts, timezone.utc)
        order._status     = OrderStatus.CLOSED

        rem_order = jsonutil.read_optional(response, 'remaining_order', dict)

        if len(rem_order) == 0:
            return None
        
        rem_order_ticket     = jsonutil.read_required(rem_order, 'ticket',     int)
        rem_order_lots       = jsonutil.read_required(rem_order, 'lots',       float)
        rem_order_comment    = jsonutil.read_required(rem_order, 'comment',    str)
        rem_order_commission = jsonutil.read_required(rem_order, 'commission', float)
        rem_order_profit     = jsonutil.read_required(rem_order, 'profit',     float)
        rem_order_swap       = jsonutil.read_required(rem_order, 'swap',       float)

        return Order(
            ticket       = rem_order_ticket,
            symbol       = order.symbol(),
            side         = order.side(),
            type         = order.type(),
            lots         = rem_order_lots,
            status       = OrderStatus.FILLED,
            open_price   = order.open_price(),
            open_time    = order.open_time(),
            stop_loss    = order.stop_loss(),
            take_profit  = order.take_profit(),
            magic_number = order.magic_number(),
            comment      = rem_order_comment,
            commission   = rem_order_commission,
            profit       = rem_order_profit,
            swap         = rem_order_swap
        )

    def modify_order(self,
                     order: Order,
                     stop_loss: float,
                     take_profit: float,
                     price: Optional[float] = None,
                     expiration: Optional[datetime] = None
    ):
        if order.is_pending():
            price = order.open_price()
            expiration = order.expiration()

        request = {
            'cmd': 'modify_order',
            'msg': {
                'ticket':     order.ticket(),
                'price':      float(price),
                'stoploss':   float(stop_loss),
                'takeprofit': float(take_profit),
                'expiration': int(expiration.timestamp())
            }
        }

        self._send_request_and_get_response(request)

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
    def _place_order(self,
                     symbol: str,
                     side: Side,
                     opcode: OperationCode,
                     lots: float,
                     price: float,
                     slippage: float,
                     stop_loss: float,
                     take_profit: float,
                     comment: Optional[str],
                     magic_number: Optional[int],
                     expiration: Optional[datetime]
    ):
        response = self._send_order_request_and_get_response(
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

        ticket = jsonutil.read_required(response, 'ticket', int)
        
        open_price = price
        status = OrderStatus.FILLED

        if opcode == OperationCode.BUY or opcode == OperationCode.SELL:
            # A market order may return its open price, since it is filled right away.
            open_price = jsonutil.read_optional(response, 'op', float)
        else:
            # A pending order may return its lots, since it may be partially filled.
            actual_lots = jsonutil.read_optional(response, 'lots', float)

            if actual_lots != float(0) and actual_lots != lots:
                status = OrderStatus.PARTIALLY_FILLED

        open_timestamp = jsonutil.read_optional(response, 'ot',         int)
        commission     = jsonutil.read_optional(response, 'commission', float)
        profit         = jsonutil.read_optional(response, 'profit',     float)
        swap           = jsonutil.read_optional(response, 'swap',       float)

        order = Order(
            ticket       = ticket,
            symbol       = symbol,
            side         = side,
            type         = OrderType.MARKET_ORDER,
            lots         = lots,
            status       = status,
            open_price   = open_price,
            open_time    = datetime.fromtimestamp(open_timestamp, timezone.utc),
            stop_loss    = stop_loss,
            take_profit  = take_profit,
            magic_number = magic_number,
            comment      = comment,
            commission   = commission,
            profit       = profit,
            swap         = swap
        )

        #TODO: add order to track later

        return order 

    def _send_order_request_and_get_response(
        self,
        symbol: str,
        opcode: OperationCode,
        lots: float,
        price: float,
        slippage: int,
        stop_loss: float,
        take_profit: float,
        comment: str,
        magic_number: int,
        expiration: Optional[datetime] = None
    ):
        request = {
            'cmd': 'place_order',
            'msg': {
                'symbol': symbol,
                'opcode': opcode.value,
                'lots':   lots,
                'price':  price
            }
        }

        if slippage != 0:
            request['msg']['slippage'] = slippage

        if stop_loss != 0.0:
            request['msg']['sl'] = stop_loss
        
        if take_profit != 0.0:
            request['msg']['tp'] = take_profit

        if comment != '':
            request['msg']['comment'] = comment

        if magic_number != 0:
            request['msg']['magic'] = magic_number
        
        if isinstance(expiration, datetime):
            request['msg']['expiration'] = int(expiration.timestamp())

        return self._send_request_and_get_response(request)

    def _wait_response_until(self, timeout_dt: datetime) -> str:
        """Receives a string response from the REQ socket.

        Waits until a string response is receives from the PULL socket or
        `timeout_dt` is reached. If the timeout is reached, raises RequestTimeout.
        """

        while datetime.now() < timeout_dt:
            try:
                response = self._req_socket.recv_string(flags=zmq.DONTWAIT)

                if response != '':
                    return response
            except zmq.error.Again:
                pass

        raise error.RequestTimeout('TODO')

    def _wait_response_for(self, timeout_ms: int) -> str:
        """
        Waits for `timeout_ms` until a response is received.
        """
        if timeout_ms < 0:
            timeout_ms = 0

        timeout_dt = datetime.now() + timedelta(0, 0, timeout_ms * 1000)

        return self._wait_response_until(timeout_dt)
    
    def _parse_response(self, cmd: str, response: str) -> dict:
        """
        Breaks down the content of a `str` response into a `dict` object.
        """

        response = json.loads(response)

        if not isinstance(response, dict):
            raise error.InvalidResponse('response of request is not of type JSON object')

        result = jsonutil.read_required(response, 'result', int)

        param = response.get('param', '')

        result = error.ErrorCode(result)

        if result == error.ErrorCode.NO_ERROR or result == error.ErrorCode.NO_MQLERROR:
            return response
        elif result == error.ErrorCode.USER_UNKNOWN_COMMAND:
            raise error.UnknownServerCommand(cmd)
        elif result == error.ErrorCode.USER_MISSING_REQUIRED_PARAM:
            raise error.MissingRequiredParameter(cmd, param)
        elif result == error.ErrorCode.USER_INVALID_PARAMETER_TYPE:
            raise error.InvalidParameterType(cmd, param)
        elif result == error.ErrorCode.USER_INVALID_PARAMETER_VALUE:
            raise error.InvalidParameterValue(cmd, param)
        else: # any(result == ec.value for ec in error.ErrorCode):
            raise error.ExecutionError(cmd, result)

    def _send_request_and_get_response(self, request: dict) -> dict:
        self._send_request(request)
        self._logger.debug('Sent request: %s', request)

        response = self._parse_response(request['cmd'], self._wait_response_for(60000))
        self._logger.debug('Received response: %s', response)

        return response
    
    def _send_request(self, _dict):
        """
        Sends commands through the PUSH socket.
        """

        try:
            self._req_socket.send_string(json.dumps(_dict), zmq.DONTWAIT)
        except zmq.error.Again:
            sleep(0.000000001)
            raise error.Again()

    def _process_event(self, msg: str):
        """Parses, validates, and notifies an event message.

        Raises
        ------
        ValueError
            If message name is unknown or message body is invalid.
        
        TypeError
            If message body is of an invalid type or has a required value of an invalid type.
        """

        msg_body_index = msg.strip().find(' ')

        if msg_body_index == -1:
            raise ValueError('could not find whitespace separator in event message')

        msg_name = msg[0:msg_body_index]

        if msg_name.startswith('tick:'):
            msg_body = msg[msg_body_index:]
            symbol, tick = self._parse_tick_event(msg_name, msg_body)

            self.tick_received.emit(symbol, tick)
        else:
            raise ValueError("event message is of unknown name '%s'" % msg_name)

    def _parse_tick_event(self, msg_name: str, msg_body: str) -> Tuple[str, Tick]:
        symbol = msg_name[len('tick:'):]

        if symbol == '':
            raise ValueError("missing instrument's symbol after tick message name")
        
        tick_array = json.loads(msg_body)

        if not isinstance(tick_array, List):
            raise TypeError("body of tick event message is of invalid type '%s' (expected: '%s')" % type(tick_array), type(List))

        if len(tick_array) != 3:
            raise ValueError('expected 3 array elements in tick event (got: %s)' % len(tick_array))

        timestamp = jsonutil.read_required_index(tick_array, 0, int)
        bid       = jsonutil.read_required_index(tick_array, 1, float)
        ask       = jsonutil.read_required_index(tick_array, 2, float)

        tick = Tick(
            server_time = datetime.fromtimestamp(timestamp, timezone.utc),
            bid         = bid,
            ask         = ask
        )

        return symbol, tick
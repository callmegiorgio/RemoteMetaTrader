import zmq
import json
import logging
from datetime import datetime, timedelta, timezone
from typing   import List, Optional, Set, Tuple, Type
from time     import sleep
from rmt      import (jsonutil, error, Order, Side, OrderType,
                      Exchange, Tick, Bar, OrderStatus)
from . import mt4

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
        request  = mt4.requests.GetTickRequest(symbol)
        response = mt4.responses.GetTickResponse(self._send_request(request))
        
        return response.tick()

    def get_bars(self,
                 symbol: str,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None
    ) -> List[Bar]:
        request  = mt4.requests.GetBarsRequest(symbol, start_time, end_time)
        response = mt4.responses.GetBarsResponse(self._send_request(request))
        
        return response.bars()

    def subscribe(self, symbol: str):
        if symbol in self._subscribed_symbols:
            return

        request = mt4.requests.WatchSymbolRequest(symbol)
        self._send_request(request)

        self._sub_socket.subscribe('tick:' + symbol)
        self._subscribed_symbols.add(symbol)

    def subscribe_all(self):
        request  = mt4.requests.WatchSymbolRequest('*')
        response = mt4.responses.WatchSymbolResponse(self._send_request(request))
        
        for symbol in response.symbols():
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
                           price: float = 0,
                           slippage: int = 0,
                           stop_loss: float = 0,
                           take_profit: float = 0,
                           comment: str = '',
                           magic_number: int = 0
    ) -> Order:
        opcode = None

        if side == Side.BUY:
            opcode = mt4.OperationCode.BUY
        elif side == Side.SELL:
            opcode = mt4.OperationCode.SELL
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
            opcode = mt4.OperationCode.BUY_LIMIT
        elif side == Side.SELL:
            opcode = mt4.OperationCode.SELL_LIMIT
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
            opcode = mt4.OperationCode.BUY_STOP
        elif side == Side.SELL:
            opcode = mt4.OperationCode.SELL_STOP
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
                    price: float = 0,
                    slippage: int = 0
    ):
        request  = mt4.requests.CloseOrderRequest(order.ticket(), float(price), int(slippage))
        response = mt4.responses.CloseOrderResponse(self._send_request(request))

        order._status      = OrderStatus.CLOSED
        order._lots        = response.lots()
        order._close_price = response.close_price()
        order._close_time  = response.close_time()
        order._comment     = response.comment()
        order._commission  = response.commission()
        order._profit      = response.profit()
        order._swap        = response.swap()

    def partial_close_order(self,
                            order: Order,
                            lots: float,
                            price: float = 0,
                            slippage: int = 0
    ) -> Order:
        request  = mt4.requests.PartialCloseOrderRequest(order.ticket(), float(lots), float(price), int(slippage))
        response = mt4.responses.PartialCloseOrderResponse(self._send_request(request))

        order._status      = OrderStatus.CLOSED
        order._lots        = response.lots()
        order._close_price = response.close_price()
        order._close_time  = response.close_time()
        order._comment     = response.comment()
        order._commission  = response.commission()
        order._profit      = response.profit()
        order._swap        = response.swap()

        if response.remaining_order_ticket() != 0:
            order = Order(
                ticket       = response.remaining_order_ticket(),
                symbol       = order.symbol(),
                side         = order.side(),
                type         = order.type(),
                lots         = response.remaining_order_lots(),
                status       = OrderStatus.FILLED,
                open_price   = order.open_price(),
                open_time    = order.open_time(),
                stop_loss    = order.stop_loss(),
                take_profit  = order.take_profit(),
                magic_number = response.remaining_order_magic_number(),
                comment      = response.remaining_order_comment(),
                commission   = response.remaining_order_commission(),
                profit       = response.remaining_order_profit(),
                swap         = response.remaining_order_swap()
            )

        return order

    def modify_order(self,
                     order: Order,
                     stop_loss: float,
                     take_profit: float,
                     price: Optional[float] = None,
                     expiration: Optional[datetime] = None
    ):
        if order.status() not in [OrderStatus.PENDING, OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED]:
            return

        request = mt4.requests.ModifyOrderRequest(
            order.ticket(),
            float(stop_loss),
            float(take_profit),
            price,
            expiration
        )

        mt4.responses.ModifyOrderResponse(self._send_request(request))

        order._stop_loss   = float(stop_loss)
        order._take_profit = float(take_profit)

        if price is not None:
            order._open_price = float(price)

        if expiration is not None:
            order._expiration = expiration

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
                     opcode: mt4.OperationCode,
                     lots: float,
                     price: float,
                     slippage: float,
                     stop_loss: float,
                     take_profit: float,
                     comment: Optional[str],
                     magic_number: Optional[int],
                     expiration: Optional[datetime]
    ):
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

        open_price = price
        status     = OrderStatus.FILLED

        if opcode in [mt4.OperationCode.BUY, mt4.OperationCode.SELL]:
            # A market order may return its open price, since it is filled right away.
            open_price = response.open_price()
        else:
            # A pending order may return its lots, since it may be partially filled.
            actual_lots = response.lots()

            if actual_lots != float(0) and actual_lots != lots:
                status = OrderStatus.PARTIALLY_FILLED

        order = Order(
            ticket       = response.ticket(),
            symbol       = symbol,
            side         = side,
            type         = OrderType.MARKET_ORDER,
            lots         = lots,
            status       = status,
            open_price   = open_price,
            open_time    = response.open_time(),
            stop_loss    = stop_loss,
            take_profit  = take_profit,
            magic_number = magic_number,
            comment      = comment,
            commission   = response.commission(),
            profit       = response.profit(),
            swap         = response.swap()
        )

        #TODO: add order to track later

        return order

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

    def _send_request(self, request: mt4.requests.Request) -> str:
        try:
            request_msg = request.serialize()

            self._req_socket.send_string(request_msg, zmq.DONTWAIT)
            self._logger.debug('Sent request: %s', request_msg)

            response = self._wait_response_for(60000)
            self._logger.debug('Received response: %s', response)

            return response
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
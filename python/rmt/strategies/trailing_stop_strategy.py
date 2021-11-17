from math   import ceil, floor
from enum   import IntFlag
from typing import Dict
from rmt    import (
    Strategy, Exchange, Tick, Bar, Order, OrderStatus,
    Side, SlottedClass, error
)

class TrailingStopPolicy(IntFlag):
    """Changes the behavior of a Trailing Stop."""

    MIN_ADVANCE_AT_OPEN_PRICE = 1
    MAX_ADVANCE_AT_OPEN_PRICE = 2
    NO_COMMISSION             = 4

class TrailingStop:
    """Interfaces the behavior of a Trailing Stop."""

    def calculate(self, order: Order, original_stop_loss: float, price_distance: float) -> float:
        """Dynamically calculates the Stop Loss price of an order.
        
        Parameters
        ----------
        order : Order
            Order associated with this Trailing Stop object.
        
        original_stop_loss : float
            Price of Stop Loss of `order` when `TrailingStopStrategy.set_trailing_stop()`
            was called for the last time.
        
        price_distance : float
            Distance from `order.open_price()` and the current market price.

        Returns
        -------
        float
            New Stop Loss price.
        """

        raise error.NotImplementedException(self.__class__, 'calculate')

class SteadyTrailingStop(TrailingStop, SlottedClass):
    """Implements a Trailing Stop with steady movements.

    Description
    -----------    
    A `SteadyTrailingStop` has two properties: an `activation_distance` and a
    `reposition_distance`, both measured as a price of the order's instrument.

    `activation_distance` defines how far from an order's open price the current
    market price has to move for the Trailing Stop to be activated. For example,
    say a buy order was filled at price 1000 and has a Stop Loss at price 990.
    If `activation_distance` is 5, that means the Trailing Stop will be activated
    when the current market price of the order's instrument reaches a multiple of
    5 after 1000, that is, it will be activated at prices 1005, 1010, 1015, 1020,
    and so on. "Activation" here simply means that an order's Stop Loss price
    will change upon calculation, rather than having no effect.
    
    `reposition_distance` defines how far from the original Stop Loss the new
    Stop Loss will move once the Trailing Stop is activated. Taking the above
    example of an order filled at 1000 with a Stop Loss at 990 and an activation
    distance of 5, if `reposition_distance` is 2, that means when the Trailing Stop
    is activated at prices 1005, 1010, 1015, and 1020, the order will have a Stop
    Loss set to prices 992, 994, 996, and 998, respectively. Hence "steady."
    """

    __slots__ = [ 
        '_activation_distance',
        '_reposition_distance',
    ]

    def __init__(self, activation_distance: float, reposition_distance: float):
        super().__init__()

        if activation_distance <= 0:
            raise ValueError('activation distance of Steady Trailing Stop must be greater than 0')
        
        self._activation_distance = activation_distance
        self._reposition_distance = reposition_distance

    @property
    def activation_distance(self) -> float:
        return self._activation_distance

    @property
    def reposition_distance(self) -> float:
        return self._reposition_distance

    def calculate(self, order: Order, original_stop_loss: float, price_distance: float) -> float:
        sl_distance_count = int(price_distance / self._activation_distance)

        sl_distance   = sl_distance_count * self._reposition_distance
        new_stop_loss = original_stop_loss + (sl_distance * order.side())

        return new_stop_loss

class TrailingStopData(SlottedClass):
    """Stores information about a Trailing Stop order."""

    __slots__ = [
        '_order',
        '_instrument',
        '_original_sl',
        '_trailing_stop',
        '_policy'
    ]

    def __init__(self,
                 order: Order,
                 original_stop_loss: float,
                 trailing_stop: TrailingStop,
                 policy: TrailingStopPolicy
    ):
        super().__init__()

        self._order         = order
        self._original_sl   = original_stop_loss
        self._trailing_stop = trailing_stop
        self._policy        = policy

    @property
    def order(self) -> Order:
        return self._order
    
    @property
    def original_stop_loss(self) -> float:
        return self._original_sl

    @property
    def trailing_stop(self) -> TrailingStop:
        return self._trailing_stop
    
    @property
    def policy(self) -> TrailingStopPolicy:
        return self._policy

class TrailingStopStrategy(Strategy):
    """Implements a strategy that supports Trailing Stop orders.
    
    A Trailing Stop allows a dynamic movement of an order's Stop Loss price as
    market price changes. The class `TrailingStopStrategy` extends `Strategy`
    so that orders placed by it may have a Trailing Stop associated with them,
    and implements a logic for updating their Stop Loss prices.

    For that, this class hooks `Strategy.tick_received` and `Strategy.bar_closed`,
    and updates the Stop Loss prices of orders tracked with `set_trailing_stop()`.

    """
    def __init__(self, exchange: Exchange, symbol: str):
        super().__init__(exchange, symbol)

        self._tick_ts_list: Dict[int, TrailingStopData] = {}
        self._bar_closed_ts_list: Dict[int, TrailingStopData] = {}

        self.tick_received.connect(self._tick_update_trailing_stops)
        self.bar_closed.connect(self._bar_update_trailing_stops)

        self.order_closed.connect(self.remove_trailing_stop)
        self.order_canceled.connect(self.remove_trailing_stop)
        self.order_expired.connect(self.remove_trailing_stop)
    
    def set_trailing_stop(self, 
                          ticket: int,
                          trailing_stop: TrailingStop,
                          policy: TrailingStopPolicy = TrailingStopPolicy(0),
                          at_bar_close: bool = False
    ):
        """Turns an order placed by this strategy into a Trailing Stop order.

        Description
        -----------
        This method turns the order identified by `ticket` into a Trailing Stop order,
        thus causing the order's Stop Loss to be calculated at every received tick or
        every bar close on this strategy's instrument, depending on `at_bar_close`.

        If `at_bar_close` is True, `trailing_stop.calculate()` is invoked at every
        closed bar of this strategy's instrument. Otherwise, it's invoked at every
        tick received.
        
        `trailing_stop.calculate()` is expected to return the new Stop Loss price
        according to the distance of the current market price from the order's open
        price. If the new Stop Loss resulting from that calculation *advances*
        (greater than, if order is buy; less than, if order is sell) the current Stop
        Loss, the current Stop Loss is updated to the new Stop Loss. Otherwise, the
        calculation has no effect. In other words, a Stop Loss cannot recede.

        The order must be of the same instrument as this strategy's instrument and must
        have a Stop Loss previously set. Otherwise, `ValueError` is raised.

        If `policy` has the flag `TrailingStopPolicy.MIN_ADVANCE_AT_OPEN_PRICE` set,
        the calculated Stop Loss is compared against the order's open price from an
        anti-trend pespective. That is, if the order is buy and the calculated Stop
        Loss is less than the order's open price, the current Stop Loss is set to the
        order's open price. Or if the order is sell and the calculated Stop Loss is
        greater than its open price, the Stop Loss is also set to the order's open
        price.

        If `policy` has the flag `TrailingStopPolicy.MAX_ADVANCE_AT_OPEN_PRICE` set,
        the calculated Stop Loss is compared against the order's open price from a
        pro-trend pespective. That is, the Stop Loss is set to the order's open price
        if either the order is a buy and the calculated Stop Loss is greater than its
        open price, or if the order is a sell and the calculated Stop Loss is less than
        its open price.

        If `policy` has the flag `TrailingStopPolicy.NO_COMMISSION` set, the calculated
        Stop Loss is added enough points to cover up the cost of the order's commission.
        For example, if the order has a commission of 0.1 USD, and the tick size of the
        order's instrument equates 1 point and is worth 0.01 USD, 10 points would be
        added to the calculated Stop Loss, such that if the resulting Stop Loss was
        reached by market, the order would incur no loss.

        Note that setting both flags `MAX_ADVANCE_AT_OPEN_PRICE` and `MIN_ADVANCE_AT_OPEN_PRICE`
        to `policy` makes the order behave as a break-even order whose Stop Loss is
        fixed to the order's open price by the time the first Stop Loss is updated.
        If `NO_COMMISSION` is also set, then the order behaves as a break-even order
        which incurs no loss.

        Raises
        ------
        ValueError
            If order's instrument is not the same as this strategy's `instrument`, or if
            order has no Stop Loss level.
        
        RMTError
            Raised by a failed call to `Strategy.get_order(ticket)`.
        """
        
        order = self.get_order(ticket)

        if order.symbol() != self.instrument.symbol:
            raise ValueError(
                "order #{0} instrument ({1}) is not same as this strategy's instrument ({2})"
                .format(ticket, order.symbol(), self.instrument.symbol)
            )

        stop_loss = order.stop_loss()

        if stop_loss is None:
            raise ValueError('order #{} has no Stop Loss level'.format(ticket))

        ts_list = self._bar_closed_ts_list if at_bar_close else self._tick_ts_list

        self.remove_trailing_stop(ticket)

        ts_list[ticket] = TrailingStopData(order, stop_loss, trailing_stop, policy)

    def remove_trailing_stop(self, ticket: int):
        try:
            del self._tick_ts_list[ticket]
        except KeyError:
            pass

        try:
            del self._bar_closed_ts_list[ticket]
        except KeyError:
            pass

    #===============================================================================
    # Internals
    #===============================================================================
    def _tick_update_trailing_stops(self, tick: Tick):
        self._update_trailing_stops_in_list(self._tick_ts_list, tick)

    def _bar_update_trailing_stops(self, bar: Bar):
        # `bar` gives us the bid price, but the ask price may also be needed
        # (if there are sell orders stored).
        tick = self.tick

        self._update_trailing_stops_in_list(self._bar_closed_ts_list, tick)

    def _update_trailing_stops_in_list(self, ts_list: Dict[int, TrailingStopData], tick: Tick):
        for ticket, ts_data in ts_list.items():
            price = tick.bid if ts_data.order.is_buy() else tick.ask

            self._update_trailing_stop(price, ticket, ts_data)

    def _update_trailing_stop(self,
                              current_price: float,
                              ticket:        int,
                              ts_data:       TrailingStopData
    ):
        order = ts_data.order
        
        if order.status() not in [OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED]:
            return

        side       = order.side()
        open_price = order.open_price()

        if (current_price * side) <= (open_price * side):
            return

        price_distance = abs(current_price - open_price)
        new_stop_loss  = ts_data.trailing_stop.calculate(order, ts_data.original_stop_loss, price_distance)

        if (new_stop_loss * side) <= (order.stop_loss() * side):
            return # cannot recede Stop Loss

        policy = ts_data.policy

        if policy & TrailingStopPolicy.MIN_ADVANCE_AT_OPEN_PRICE:
            if order.is_buy():
                new_stop_loss = max(new_stop_loss, open_price)
            else:
                new_stop_loss = min(new_stop_loss, open_price)
        
        if policy & TrailingStopPolicy.MAX_ADVANCE_AT_OPEN_PRICE:
            if order.is_buy():
                new_stop_loss = min(new_stop_loss, open_price)
            else:
                new_stop_loss = max(new_stop_loss, open_price)

        if (policy & TrailingStopPolicy.NO_COMMISSION) and (order.commission() != 0):
            commission_price = abs(order.commission())

            if self.instrument.quote_currency != self._exchange.account.currency:
                rate = self._exchange.get_exchange_rate(
                    self.instrument.quote_currency,
                    self._exchange.account.currency
                )

                commission_price *= rate

            coverage_price_distance = commission_price / order.lots()
            coverage_price          = order.open_price() + (coverage_price_distance * side)
            
            if (new_stop_loss * side) < (coverage_price * side):
                # This computation is for the case the coverage price is not a multiple of
                # the instrument's tick size. For example, if the coverage price is 1000 and
                # the instrument's tick size is 0.03, there needs to be a price adjustment,
                # since 1000 is not a multiple of 0.03.
                # 
                # As the goal is to cover up the commission price, we take the next multiple
                # of tick size after the coverage price if side is buy, or the previous
                # multiple before the coverage price if side is sell. In the above example,
                # the next multiple of 0.03 after 1000 is 1000.02, and the previous multiple
                # of 0.03 before 1000 is 999.99, which would be used on a buy or sell order,
                # respectively.
                #
                # In practice, this computation is mostly redundant, since most instruments
                # will have a tick size of 0.01, but it's necessary nonetheless.
                if side == Side.BUY:
                    new_stop_loss = ceil(coverage_price / self.instrument.tick_size) * self.instrument.tick_size
                else:
                    new_stop_loss = floor(coverage_price / self.instrument.tick_size) * self.instrument.tick_size

        if (new_stop_loss * side) >= (current_price * side):
           return # cannot place Stop Loss at market price or above market price

        try:
            self.modify_order(ticket, stop_loss = self.instrument.normalize_price(new_stop_loss))
        except error.RMTError as e:
            print('_update_trailing_stop:', str(e))
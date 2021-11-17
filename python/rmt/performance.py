from typing import List
from .      import Order, OrderStatus, SlottedClass

class Performance(SlottedClass):
    """Measures the performance of closed orders and stores the result."""

    __slots__ = [
        '_sl_count',
        '_sg_count',
        '_tp_count',
        '_loss_count',
        '_gain_count',
        '_even_count',
        '_gross_sl',
        '_gross_sg',
        '_gross_tp',
        '_gross_loss',
        '_gross_gain'
    ]

    def __init__(self, orders: List[Order], decimal_places: int):
        self._sl_count   = 0
        self._sg_count   = 0
        self._tp_count   = 0
        self._loss_count = 0
        self._gain_count = 0
        self._even_count = 0
        self._gross_sl   = 0
        self._gross_sg   = 0
        self._gross_tp   = 0
        self._gross_loss = 0
        self._gross_gain = 0

        for order in orders:
            if order.status != OrderStatus.CLOSED:
                continue

            profit = round(order.profit + order.commission + order.swap, 8)

            if profit == 0:
                self._even_count += 1
                continue

            tp = order.take_profit
            sl = order.stop_loss
            close_price = order.close_price

            if profit < 0:
                self._loss_count += 1
                self._gross_loss += profit

                if sl is None:
                    continue

                if ((order.is_buy()  and close_price <= sl) or
                    (order.is_sell() and close_price >= sl)):
                    self._sl_count += 1
                    self._gross_sl += profit

            else:
                self._gain_count += 1
                self._gross_gain += profit

                if tp is not None:
                    if ((order.is_buy()  and close_price >= tp) or
                        (order.is_sell() and close_price <= tp)):
                        self._tp_count += 1
                        self._gross_tp += profit

                elif sl is not None:
                    open_price = order.open_price

                    if ((order.is_buy()  and sl > open_price and close_price >= sl) or
                        (order.is_sell() and sl < open_price and close_price <= sl)):
                        self._sg_count += 1
                        self._gross_sg += profit
            
        self._gross_sl   = round(self._gross_sl,   decimal_places)
        self._gross_sg   = round(self._gross_sg,   decimal_places)
        self._gross_tp   = round(self._gross_tp,   decimal_places)
        self._gross_loss = round(self._gross_loss, decimal_places)
        self._gross_gain = round(self._gross_gain, decimal_places)

    @property
    def trade_count(self) -> int:
        """Amount of closed trades."""

        return self._loss_count + self._gain_count + self._even_count

    @property
    def stop_loss_count(self) -> int:
        """Amount of trades closed by Stop Loss."""

        return self._sl_count

    @property
    def stop_gain_count(self) -> int:
        """Amount of trades closed by Stop Gain."""

        return self._sg_count

    @property
    def take_profit_count(self) -> int:
        """Amount of trades closed by Take Profit."""

        return self._tp_count
    
    @property
    def loss_trade_count(self) -> int:
        """Amount of trades with profit less than 0."""

        return self._loss_count

    @property
    def gain_trade_count(self) -> int:
        """Amount of trades with profit greater than 0."""

        return self._gain_count

    @property
    def even_trade_count(self) -> int:
        """Amount of trades with profit equal to 0."""

        return self._even_count

    @property
    def gross_stop_loss(self) -> float:
        """Sum of losses of all trades closed by Stop Loss."""

        return self._gross_sl

    @property
    def gross_stop_gain(self) -> float:
        """Sum of gains of all trades closed by Stop Gain."""

        return self._gross_sg

    @property
    def gross_take_profit(self) -> float:
        """Sum of gains of all trades closed by Take Profit."""

        return self._gross_tp

    @property
    def gross_loss(self) -> float:
        """Sum of losses of all trades with profit less than 0."""

        return self._gross_loss

    @property
    def gross_gain(self) -> float:
        """Sum of gains of all trades with profit greater than 0."""

        return self._gross_gain

    def gross_profit(self) -> float:
        """Sum of gross gain and gross loss."""

        return self._gross_gain + self._gross_loss
from typing import List
from .      import Order, OrderStatus, SlottedClass

class Performance(SlottedClass):
    """Measures the performance of closed orders and stores the result."""

    __slots__ = [
        '_sl_count',
        '_sg_count',
        '_tp_count',
        '_tl_count',
        '_loss_count',
        '_gain_count',
        '_even_count',
        '_gross_sl',
        '_gross_sg',
        '_gross_tp',
        '_gross_tl',
        '_gross_loss',
        '_gross_gain',
        '_gross_profit'
    ]

    def __init__(self, orders: List[Order], decimal_places: int):
        self._sl_count   = 0
        self._sg_count   = 0
        self._tp_count   = 0
        self._tl_count   = 0
        self._loss_count = 0
        self._gain_count = 0
        self._even_count = 0
        self._gross_sl   = 0
        self._gross_sg   = 0
        self._gross_tp   = 0
        self._gross_tl   = 0
        self._gross_loss = 0
        self._gross_gain = 0

        for order in orders:
            if order.status != OrderStatus.CLOSED:
                continue

            profit = round(order.profit + order.commission + order.swap, 8)

            if profit == 0:
                self._even_count += 1
                continue

            side        = order.side
            tp          = order.take_profit
            sl          = order.stop_loss
            open_price  = order.open_price
            close_price = order.close_price

            sided_tp          = None if tp is None else tp * side
            sided_sl          = None if sl is None else sl * side
            sided_open_price  = open_price * side
            sided_close_price = close_price * side

            if profit < 0:
                self._loss_count += 1
                self._gross_loss += profit

                if tp is not None and (sided_tp <= sided_open_price) and (sided_close_price >= sided_tp):
                    self._tl_count += 1
                    self._gross_tl += profit

                elif sl is not None and (sided_close_price <= sided_sl):
                    self._sl_count += 1
                    self._gross_sl += profit

            else:
                self._gain_count += 1
                self._gross_gain += profit

                if tp is not None and (sided_close_price >= sided_tp):
                    self._tp_count += 1
                    self._gross_tp += profit

                elif sl is not None and (sided_sl >= sided_open_price) and (sided_close_price <= sided_sl):
                    self._sg_count += 1
                    self._gross_sg += profit

        self._gross_sl     = round(self._gross_sl,   decimal_places)
        self._gross_sg     = round(self._gross_sg,   decimal_places)
        self._gross_tp     = round(self._gross_tp,   decimal_places)
        self._gross_tl     = round(self._gross_tl,   decimal_places)
        self._gross_loss   = round(self._gross_loss, decimal_places)
        self._gross_gain   = round(self._gross_gain, decimal_places)
        self._gross_profit = round(self._gross_gain + self._gross_loss, decimal_places)

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
    def take_loss_count(self) -> int:
        """Amount of trades closed by Take Profit."""

        return self._tl_count
    
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
    def gross_take_loss(self) -> float:
        """Sum of losses of all trades closed by Take Loss."""

        return self._gross_tl

    @property
    def gross_loss(self) -> float:
        """Sum of losses of all trades with profit less than 0."""

        return self._gross_loss

    @property
    def gross_gain(self) -> float:
        """Sum of gains of all trades with profit greater than 0."""

        return self._gross_gain

    @property
    def gross_profit(self) -> float:
        """Sum of gross gain and gross loss."""

        return self._gross_profit

    def __str__(self) -> str:
        success_rate = 0
        noneven_count = self.gain_trade_count + self.loss_trade_count
        
        if noneven_count > 0:
            success_rate = self.gain_trade_count / noneven_count

        return (
            'Performance(profit: {} - {} = {}, trades: {} ({} gain + {} loss + {} even), success rate: {}%, SL: {} ({}), SG: {} ({}), TP: {} ({}), TL: {} ({})'
            .format(
                self.gross_gain, abs(self.gross_loss), self.gross_profit,
                self.trade_count, self.gain_trade_count, self.loss_trade_count, self.even_trade_count,
                round(success_rate * 100, 2),
                self.stop_loss_count,   self.gross_stop_loss,
                self.stop_gain_count,   self.gross_stop_gain,
                self.take_profit_count, self.gross_take_profit,
                self.take_loss_count,   self.gross_take_loss
            )
        )
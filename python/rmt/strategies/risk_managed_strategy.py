from datetime import datetime
from typing   import Optional
from rmt      import Strategy, Exchange, Side, Order, OrderType, error

class RiskCalculator:
    def calculate(self, balance: float) -> float:
        raise error.NotImplementedException(self.__class__, 'calculate')

class PercentRiskCalculator(RiskCalculator):
    def __init__(self, percent: float) -> None:
        super().__init__()

        if percent <= 0 or percent > 100:
            raise ValueError('risk percent must in range (0, 100] (got: {})'.format(percent))

        self._percent_ratio = percent / 100

    def calculate(self, balance: float) -> float:
        return balance * self._percent_ratio

    def __str__(self) -> str:
        return 'PercentRiskCalculator(percent={}%)'.format(self._percent_ratio * 100)

class FixedRiskCalculator(RiskCalculator):
    def __init__(self, amount: float) -> None:
        super().__init__()

        if amount <= 0:
            raise ValueError('risk amount must be greater than 0 (got: {})'.format(amount))

        self._amount = amount
    
    def calculate(self, balance: float) -> float:
        return self._amount

    def __str__(self) -> str:
        return 'FixedRiskCalculator(amount={})'.format(self._amount)

class RiskManagedStrategy(Strategy):
    """Implements a risk-managed strategy."""

    def __init__(self, exchange: Exchange, symbol: str):
        super().__init__(exchange, symbol)

        self._risk_calculator = RiskCalculator()

    def available_balance(self) -> float:
        """Balance available to place orders.
        
        This method may be overloaded by subclasses to change the amount of money allowed
        to be used by this strategy. If the method is overloaded, the returning value is
        clamped to range [0, account balance].
        """

        return self.account.balance

    @property
    def risk_calculator(self) -> RiskCalculator:
        return self._risk_calculator

    def set_risk_calculator(self, calculator: RiskCalculator):
        self._risk_calculator = calculator

    def risk_price(self) -> float:
        """Returns the risk price, in account currency, calculated by this strategy's risk calculator."""

        balance = min(max(self.available_balance(), 0), self.account.balance)
        balance = float(balance)

        risk_price = self._risk_calculator.calculate(balance)

        # TODO: don't assume account currency has 2 digits
        return round(risk_price, 2)

    def place_order_on_risk(self,
                            side:         Side,
                            order_type:   OrderType,
                            price:        float,
                            stop_loss:    float,
                            take_profit:  Optional[float] = None,
                            slippage:     Optional[int]   = None,
                            comment:      str = '',
                            magic_number: int = 0,
                            expiration:   Optional[datetime] = None
    ) -> Order:
        open_price     = float(price)
        stop_loss      = float(stop_loss)
        max_risk_price = self.risk_price()

        exchange_rate = 1.0

        if self.instrument.quote_currency != self.account.currency:
            exchange_rate = self.get_exchange_rate(
                self.account.currency,
                self.instrument.quote_currency
            )

        max_risk_price = self.instrument.normalize_price(max_risk_price * exchange_rate)
        lots           = self._calculate_lots(max_risk_price, open_price, stop_loss)

        order = self.place_order(
            side         = side,
            order_type   = order_type,
            lots         = lots,
            price        = open_price,
            slippage     = slippage,
            stop_loss    = stop_loss,
            take_profit  = take_profit,
            comment      = comment,
            magic_number = magic_number,
            expiration   = expiration,
            symbol       = self.instrument.symbol
        )

        # The calculated risk may result in a lot size greater than `self.instrument.max_lot`,
        # in which case the lot size is clamped down to the maximum lot. However, that means
        # we haven't placed an order at `max_risk_price`, so the actual risk price must be
        # recalculated. For example, say the account balance is $1,000,000 and risk price is
        # 10% of that. The calculated lot for $100,000 may result in a lot size of 1000 or
        # so, but some instruments only support up to 500 lots, so that won't be possible.
        # `actual_risk_price` will calculate the actual amount of money which was put at risk.
        actual_risk_price = self.instrument.normalize_price(abs(order.open_price - order.stop_loss) * lots)
        
        if self.instrument.quote_currency == self.account.currency:
            # If instrument's quote currency is same as account currency, print risk price as-is.
            actual_risk_price_str = '{} {}'.format(actual_risk_price, self.account.currency)
        else:
            # Example: for instrument HK50 with an account currency of USD, this will print,
            # "100 USD (778 HKD)".
            actual_risk_price_str = '{} {} ({} {})'.format(
                round(actual_risk_price / exchange_rate, 2), # TODO: don't assume 2 decimal places
                self.account.currency,
                actual_risk_price,
                self.instrument.quote_currency
            )

        self.logger.info(
            'placed %s %s at price %f with risk price of %s on risk calculator %s',
            side.name.lower(),
            order_type.name.lower().replace('_', ' '),
            order.open_price,
            actual_risk_price_str,
            self.risk_calculator
        )

        return order

    def _calculate_lots(self, risk_price: float, open_price: float, stop_loss: float) -> float:
        price_distance = self.instrument.normalize_price(abs(open_price - stop_loss))
        point_distance = int(price_distance / self.instrument.point)

        cost_of_1_lot = point_distance * self.instrument.point_value
        risk_lot_size = risk_price / cost_of_1_lot
        
        lots = self.instrument.normalize_lots(risk_lot_size)

        return lots
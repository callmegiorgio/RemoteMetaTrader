from datetime import datetime
from typing   import Optional
from rmt      import Strategy, Exchange, Side, OrderType, error

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

class FixedRiskCalculator(RiskCalculator):
    def __init__(self, amount: float) -> None:
        super().__init__()

        if amount <= 0:
            raise ValueError('risk amount must be greater than 0 (got: {})'.format(amount))

        self._amount = amount
    
    def calculate(self, balance: float) -> float:
        return self._amount

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
        balance = min(max(self.available_balance(), 0), self.account.balance)
        balance = float(balance)

        risk_price = self._risk_calculator.calculate(balance)

        if self.instrument.quote_currency != self.account.currency:
            # Note: if `Exchange` is `MetaTrader4`, and the Expert Server is run by
            # Strategy Tester, the call below fails. MT4 doesn't support multi-currency
            # testing, so we can't exchange rates here, and thus this method is unable
            # to calculate the risk price in the instrument's quote currency.
            # 
            # A workaround, for the time being, is to comment the below call and hard-code
            # the exchange rate yourself. For instance, if `self.instrument` is US100
            # (in which case `self.instrument.quote_currency` is USD) and the account
            # currency is EUR, you must set the bid price of EURUSD yourself:
            #
            # rate = EURUSD bid price
            #
            # Argh, if only MT4 made our testing lives easier...

            rate = self.get_exchange_rate(
                self.account.currency,
                self.instrument.quote_currency
            )

            risk_price *= rate

        return self.instrument.normalize_price(risk_price)

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
    ) -> int:
        price     = float(price)
        stop_loss = float(stop_loss)

        lots = self._calculate_lots(price, stop_loss)

        ticket = self.place_order(
            side         = side,
            order_type   = order_type,
            lots         = lots,
            price        = price,
            slippage     = slippage,
            stop_loss    = stop_loss,
            take_profit  = take_profit,
            comment      = comment,
            magic_number = magic_number,
            expiration   = expiration,
            symbol       = self.instrument.symbol
        )

        return ticket

    def _calculate_lots(self, price: float, stop_loss: float) -> float:
        risk_price = self.risk_price()

        price_distance = self.instrument.normalize_price(abs(price - stop_loss))
        point_distance = int(price_distance / self.instrument.point)

        cost_of_1_lot = point_distance * self.instrument.point_value
        risk_lot_size = risk_price / cost_of_1_lot
        
        lots = self.instrument.normalize_lots(risk_lot_size)

        return lots
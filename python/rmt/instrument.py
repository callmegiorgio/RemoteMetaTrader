from pprint import pformat

class Instrument:
    """Stores static information about a trading instrument.
    
    The class `Instrument` wraps around information about a trading instrument
    that is not subject to market changes. Dynamic information, such as its bid
    and ask prices, must be retrieved from an `Exchange`.
    """

    def __init__(self,
                 symbol: str,
                 description: str,
                 base_currency: str,
                 profit_currency: str,
                 margin_currency: str,
                 decimal_places: int,
                 point: float,
                 tick_size: float,
                 contract_size: float,
                 lot_step: float,
                 min_lot: float,
                 max_lot: float,
                 min_stop_level: int,
                 freeze_level: int,
                 spread: int
    ):
        self._symbol          = symbol
        self._description     = description
        self._base_currency   = base_currency
        self._profit_currency = profit_currency
        self._margin_currency = margin_currency
        self._decimal_places  = decimal_places
        self._point           = point
        self._tick_size       = tick_size
        self._contract_size   = contract_size
        self._lot_step        = lot_step
        self._min_lot         = min_lot
        self._max_lot         = max_lot
        self._min_stop_lvl    = min_stop_level
        self._freeze_lvl      = freeze_level
        self._spread          = spread

    @property
    def symbol(self) -> str:
        """String identifier of the instrument."""

        return self._symbol

    @property
    def description(self) -> str:
        """Description of the instrument."""

        return self._description

    @property
    def base_currency(self) -> str:
        """Base currency of the instrument."""

        return self._base_currency

    @property
    def profit_currency(self) -> str:
        """Profit currency of the instrument."""

        return self._profit_currency

    @property
    def margin_currency(self) -> str:
        """Margin currency of the instrument."""

        return self._margin_currency

    @property
    def decimal_places(self) -> int:
        """Number of digits after the decimal point."""

        return self._decimal_places

    @property
    def digits(self) -> int:
        """Same as `decimal_places`."""

        return self.decimal_places

    @property
    def point(self) -> float:
        """Smallest price of the instrument.
        
        A point is the smallest price that an instrument may have. For instance, if an
        instrument has 3 digits after the decimal point, that instrument's point value
        is 0.001. Similarly, if an instrument has 2 decimal places, that instrument's
        point value is 0.01. If an instrument has no decimal places, its point value is 1.

        As such, `point` is same as `1 / (10 ** decimal_places)`.
        """

        return self._point

    @property
    def tick_size(self) -> float:
        """Smallest possible price change of the instrument.

        A trading instrument has price movements of varying lengths, with its tick size
        defining the minimum amount that its price can move up or down on an exchange.
        For instance, if an instrument's price is at 1000.42 and its tick size is 0.02,
        a tick of that instrument will only occur at a price which is below 1000.41 or
        above 1000.43. It cannot occur at prices 1000.41 or 1000.43.

        As such, a tick size defines the price change requirement for a tick to occur.
        Every time a tick of an instrument is received, that means that the difference
        between the instrument's new price and its previous price is at least the
        instrument's tick size.

        Usually, an instrument's tick size is same as its `point` value, but it not
        necessarily is. Some brokers, for instance, define different values of tick
        sizes and point values for metal and index instruments.
        
        In any case, an instrument's tick size is always a multiple of that instrument's
        point value, and orders placed on the instrument must always be a multiple of its
        tick size.
        """

        return self._tick_size

    @property
    def contract_size(self) -> float:
        """Number of base units that comprise 1 lot of the asset."""

        return self._contract_size

    @property
    def lot_step(self) -> float:
        """Smallest possible change in lot size.
        
        Orders placed on the instrument must be a multiple of its lot step.
        """

        return self._lot_step

    @property
    def min_lot(self) -> float:
        """Minimum lot allowed to place an order on the instrument."""

        return self._min_lot

    @property
    def max_lot(self) -> float:
        """Maximum lot allowed to place an order on the instrument."""

        return self._max_lot

    @property
    def min_stop_level(self) -> int:
        """Minimum distance in points allowed to place Stop orders."""

        return self._min_stop_lvl

    @property
    def freeze_level(self) -> int:
        """Distance in points to freeze trade operations."""

        return self._freeze_lvl
    
    @property
    def spread(self) -> int:
        """Spread of the instrument for instruments with fixed spread.
        
        If the instrument has a floating spread, evaluates to 0. Otherwise,
        evaluates to the instrument's spread.
        """

        return self._spread

    def is_floating_spread(self) -> bool:
        """Returns whether the instrument has floating spread."""

        return self.spread == 0

    def __repr__(self) -> str:
        return pformat(vars(self), indent=4, width=1)
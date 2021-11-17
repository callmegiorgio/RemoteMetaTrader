from rmt import SlottedClass

class Instrument(SlottedClass):
    """Stores static information about a trading instrument.
    
    The class `Instrument` wraps around information about a trading instrument
    that is not subject to market changes. Dynamic information, such as its bid
    and ask prices, must be retrieved from an `Exchange`.
    """

    __slots__ = [
        '_symbol',
        '_description',
        '_base_currency',
        '_quote_currency',
        '_margin_currency',
        '_decimal_places',
        '_point',
        '_tick_size',
        '_contract_size',
        '_lot_step',
        '_min_lot',
        '_max_lot',
        '_min_stop_lvl',
        '_freeze_lvl',
        '_spread'
    ]

    def __init__(self,
                 symbol: str,
                 description: str,
                 base_currency: str,
                 quote_currency: str,
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
        self._quote_currency  = quote_currency
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
        """String identifier of this instrument."""

        return self._symbol

    @property
    def description(self) -> str:
        """Description of this instrument."""

        return self._description

    @property
    def base_currency(self) -> str:
        """Base currency of this instrument."""

        return self._base_currency

    @property
    def profit_currency(self) -> str:
        """Same as `quote_currency`."""

        return self._quote_currency

    @property
    def quote_currency(self) -> str:
        """Quote currency of this instrument."""

        return self._quote_currency

    @property
    def margin_currency(self) -> str:
        """Margin currency of this instrument."""

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
        """Smallest price of this instrument.
        
        A point is the smallest price that an instrument may have. For instance, if an
        instrument has 3 digits after the decimal point, that instrument's point value
        is 0.001. Similarly, if an instrument has 2 decimal places, that instrument's
        point value is 0.01. If an instrument has no decimal places, its point value is 1.

        As such, `point` is same as `1 / (10 ** decimal_places)`.
        """

        return self._point

    @property
    def pip(self) -> float:
        """Unit of measurement of a price change on this instrument.

        Description
        -----------
        The standard way of quoting trading instruments is to 2 or 4 decimal places.
        However, some brokers have more granularity for quotes on certain instruments,
        such as Forex pairs, and provide quotes for them to 3 or 5 decimal places instead.
        These are known as *3-digit brokers* and *5-digit brokers*, respectively.

        For standard 2/4-digit brokers, a pip is same as a point, that is, both values
        measure the smallest price of an instrument. Conversely, for 3/5-digit brokers,
        a point is a tenth of a pip. For instance, the point and pip of EURUSD are both
        0.0001 if that instrument is quoted by a 4-digit broker. On the other hand, if
        quoted by a 5-digit broker, the point and pip of EURUSD is 0.00001 and 0.0001,
        respectively.

        In general, trading instruments on all types of brokers typically have 0, 2, 3,
        4, or 5 decimal places. It's uncommon for a trading instrument to have 1 decimal
        place or more than 5 decimal places. As such, this property assumes that if this
        instrument has an odd number of decimal places, fractional pips are being quoted
        and it will thus evaluate to 10 times a `point`. Otherwise, it evaluates to same
        as a `point`.
        """

        return self.point * pow(10, self.decimal_places % 2)

    @property
    def tick_size(self) -> float:
        """Smallest possible price change on this instrument.

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
        sizes and point for metal and index instruments.
        
        In any case, an instrument's tick size is always a multiple of that instrument's
        point, and orders placed on the instrument must always be a multiple of its tick
        size.
        """

        return self._tick_size

    @property
    def contract_size(self) -> float:
        """Number of units in `base_currency` that comprise 1 lot of the asset.
        
        For instance, if this instrument is EURUSD and `contract_size` is 100000, that
        means filling an order with a lot size of 1 is equivalent to owning 100000 EUR.
        """

        return self._contract_size

    @property
    def point_value(self) -> float:
        """Value of a point in this instrument's quote currency."""

        return self._contract_size * self.point

    @property
    def tick_value(self) -> float:
        """Value of a tick in this instrument's quote currency.
        
        Description
        -----------
        `tick_value` measures how much one tick of this instrument is worth in its quote
        currency.

        For instance, if `tick_size` is 0.01, `tick_value` is 1, and `quote_currency` 
        is USD, that means every movement of 0.01 on this instrument's price is worth
        1 USD. Similarly, if `tick_size` is 0.05, `tick_value` is 100, and `quote_currency`
        is JPY, that means every movement of 0.05 on this instrument's price is worth
        100 JPY. In the former example, `point_value` is same as `tick_value`, whereas
        in the latter, `point_value` is 5 times less than `tick_value`, that is, a move
        of one point on this instrument is worth 20 JPY.
        """

        return self._contract_size * self._tick_size

    @property
    def pip_value(self) -> float:
        """Value of a pip in this instrument's quote currency."""

        return self._contract_size * self.pip

    @property
    def lot_step(self) -> float:
        """Smallest possible change in lot size.
        
        Orders placed on this instrument must be a multiple of its lot step.
        """

        return self._lot_step

    @property
    def min_lot(self) -> float:
        """Minimum lot allowed to place an order on this instrument."""

        return self._min_lot

    @property
    def max_lot(self) -> float:
        """Maximum lot allowed to place an order on this instrument."""

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
        """Spread of this instrument if it has fixed spread.
        
        If this instrument has a floating spread, evaluates to 0. Otherwise,
        evaluates to this instrument's fixed spread.
        """

        return self._spread

    def is_floating_spread(self) -> bool:
        """Returns whether this instrument has floating spread."""

        return self.spread == 0

    def normalize_price(self, price: float) -> float:
        """Rounds `price` to this instrument's decimal places."""

        return round(price, self.decimal_places)

    def normalize_lots(self, lots: float) -> float:
        """Rounds `lots` to a multiple of `lot_step` and clamps the result to range
        [`min_lot`, `max_lot`].
        """

        # TODO: find out lot step digits.
        lots = round(lots, 2)
        lots = int(lots / self.lot_step) * self.lot_step
        lots = round(lots, 2)

        return max(min(lots, self.max_lot), self.min_lot)
#property strict

class Bar {
public:
    static bool at(string symbol, ENUM_TIMEFRAMES timeframe, uint index, Bar& bar);
    static bool current(string symbol, ENUM_TIMEFRAMES timeframe, Bar& bar);

    Bar();
    Bar(datetime time, double open, double high, double low, double close, long volume);
    Bar(const Bar& other);

    datetime time() const;
    double open() const;
    double high() const;
    double low() const;
    double close() const;
    long volume() const;

    Bar* operator=(const Bar& other);

private:
    datetime m_time;
    double   m_open;
    double   m_high;
    double   m_low;
    double   m_close;
    long     m_volume;
};

//===========================================================================
// --- Bar implementation ---
//===========================================================================
static bool Bar::at(string symbol, ENUM_TIMEFRAMES timeframe, uint index, Bar& bar)
{
    ResetLastError();

    const datetime time   = iTime  (symbol, timeframe, index); if (time == 0)   return false;
    const double   open   = iOpen  (symbol, timeframe, index); if (open == 0)   return false;
    const double   high   = iHigh  (symbol, timeframe, index); if (high == 0)   return false;
    const double   low    = iLow   (symbol, timeframe, index); if (low == 0)    return false;
    const double   close  = iClose (symbol, timeframe, index); if (close == 0)  return false;
    const long     volume = iVolume(symbol, timeframe, index); if (volume == 0) return false;

    bar.m_time   = time;
    bar.m_open   = open;
    bar.m_high   = high;
    bar.m_low    = low;
    bar.m_close  = close;
    bar.m_volume = volume;

    return true;
}

static bool Bar::current(string symbol, ENUM_TIMEFRAMES timeframe, Bar& bar)
{
    return Bar::at(symbol, timeframe, 0, bar);
}

Bar::Bar()
{
    m_time   = 0;
    m_open   = 0;
    m_high   = 0;
    m_low    = 0;
    m_close  = 0;
    m_volume = 0;
}

Bar::Bar(datetime time, double open, double high, double low, double close, long volume)
{
    m_time   = time;
    m_open   = open;
    m_high   = high;
    m_low    = low;
    m_close  = close;
    m_volume = volume;
}

Bar::Bar(const Bar& other)
{
    this.operator=(other);
}

datetime Bar::time() const
{
    return m_time;
}

double Bar::open() const
{
    return m_open;
}

double Bar::high() const
{
    return m_high;
}

double Bar::low() const
{
    return m_low;
}

double Bar::close() const
{
    return m_close;
}

long Bar::volume() const
{
    return m_volume;
}

Bar* Bar::operator=(const Bar& other)
{
    m_time   = other.m_time;
    m_open   = other.m_open;
    m_high   = other.m_high;
    m_low    = other.m_low;
    m_close  = other.m_close;
    m_volume = other.m_volume;

    return GetPointer(this);
}
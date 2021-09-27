#property strict

class Tick {
public:
    static bool current(string symbol, Tick& tick);

    Tick(datetime server_time = 0, double bid = 0, double ask = 0);

    datetime server_time() const;
    double bid() const;
    double ask() const;

    void operator=(const Tick& other);
    bool operator==(const Tick& other) const;
    bool operator!=(const Tick& other) const;

private:
    datetime m_server_time;
    double   m_bid;
    double   m_ask;
};

//===========================================================================
// --- Tick implementation ---
//===========================================================================
static bool Tick::current(string symbol, Tick& tick)
{
    if (symbol == Symbol())
    {
        RefreshRates();

        tick.m_server_time = TimeCurrent();
        tick.m_bid         = Bid;
        tick.m_ask         = Ask;
    }
    else
    {
        if (IsTesting())
            return false;

        if (!SymbolSelect(symbol, true))
            return false;
        
        MqlTick last_tick;

        if (!SymbolInfoTick(symbol, last_tick))
            return false;

        tick.m_server_time = last_tick.time;
        tick.m_bid         = last_tick.bid;
        tick.m_ask         = last_tick.ask;
    }

    return true;
}

Tick::Tick(datetime server_time, double bid, double ask)
{
    m_server_time = server_time;
    m_bid         = bid;
    m_ask         = ask;
}

datetime Tick::server_time() const
{
    return m_server_time;
}

double Tick::bid() const
{
    return m_bid;
}

double Tick::ask() const
{
    return m_ask;
}

void Tick::operator=(const Tick& other)
{
    this.m_server_time = other.m_server_time;
    this.m_bid         = other.m_bid;
    this.m_ask         = other.m_ask;
}

bool Tick::operator==(const Tick& other) const
{
    return (
        this.m_server_time == other.m_server_time &&
        this.m_bid         == other.m_bid &&
        this.m_ask         == other.m_ask
    );
}

bool Tick::operator!=(const Tick& other) const
{
    return !(this.operator==(other));
}
#property strict

// Local
#include "../Utility/sleep.mqh"

class Tick {
public:
    static bool current(string symbol, Tick& tick);

    Tick();
    Tick(datetime server_time, double bid, double ask);
    Tick(const Tick& other);

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

        long is_symbol_selected;

        // See if symbol is already selected. If we failed to get the information,
        // assume it's not selected.
        if (!SymbolInfoInteger(symbol, SYMBOL_SELECT, is_symbol_selected))
            is_symbol_selected = 0;

        if (!SymbolSelect(symbol, true))
            return false;
        
        MqlTick last_tick;

        // The function `SymbolInfoTick()` only works for symbols selected in the Market
        // Watch window. Which is what we have just done above by calling `SymbolSelect()`.
        //
        // However, it happens that immediately after selecting a symbol, MQL will most
        // of the times return a `MqlTick` with zeroed members, because will have not
        // been received from the trade server yet.
        //
        // So, what the following logic does is sleep for `sleep_msec_step` until either
        // data is received from the trade server or `max_sleep_msec` is reached.
        const uint max_sleep_msec  = 1000;
        const uint sleep_msec_step = 10;

        for (uint i = 0; i < max_sleep_msec; i += sleep_msec_step)
        {
            if (!SymbolInfoTick(symbol, last_tick))
                return false;

            // If at least one data member of `MqlTick` is not zeroed, that means
            // we got data.
            if (last_tick.time != 0)
            {
                tick.m_server_time = last_tick.time;
                tick.m_bid         = last_tick.bid;
                tick.m_ask         = last_tick.ask;

                break;
            }

            sleep(sleep_msec_step);
        }

        // If symbol was not selected at first, and we made it selected, unselect it.
        // Let's not clutter the Market Watch window, shall we?
        if (!is_symbol_selected)
            SymbolSelect(symbol, false);
    }

    return true;
}

Tick::Tick()
{
    m_server_time = 0;
    m_bid         = 0;
    m_ask         = 0;
}

Tick::Tick(datetime server_time, double bid, double ask)
{
    m_server_time = server_time;
    m_bid         = bid;
    m_ask         = ask;
}

Tick::Tick(const Tick& other)
{
    this.operator=(other);
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
#property strict

// 3rdparty
#include <Mql/Collection/Vector.mqh>

// Local
#include "../Utility/Optional.mqh"
#include "Tick.mqh"

class Instrument {
public:
    Instrument(string symbol);
    Instrument(const Instrument& other);

    Tick tick() const;
    double bid() const;
    double ask() const;

    bool convert_bid(string currency, double& dest) const;
    bool convert_ask(string currency, double& dest) const;

    string base_currency() const;
    string quote_currency() const;

    bool is_forex() const;

    Instrument* operator=(const Instrument& other);

private:
    bool convert_price(string currency, double price, double& dest) const;

    string currency(int type) const;

    string m_symbol;
    string m_base_currency;
    string m_quote_currency;
};

bool find_forex_instrument(OptionalComplex<Instrument>& instrument, string currency_a, string currency_b, bool enforce_order = false)
{
    const uint symbol_count = SymbolsTotal(false);

    for (uint i = 0; i < symbol_count; i++)
    {
        const string symbol = SymbolName(i, false);

        Instrument fx_instrument(symbol);

        if (!fx_instrument.is_forex())
            continue;

        if (fx_instrument.base_currency() == currency_a && fx_instrument.quote_currency() == currency_b)
        {
            instrument = fx_instrument;
            return true;
        }

        if (!enforce_order && fx_instrument.base_currency() == currency_b && fx_instrument.quote_currency() == currency_a)
        {
            instrument = fx_instrument;
            return true;
        }
    }

    return false;
}

//===========================================================================
// --- Instrument implementation ---
//===========================================================================
Instrument::Instrument(string symbol)
{
    m_symbol         = symbol;
    m_base_currency  = currency(SYMBOL_CURRENCY_BASE);
    m_quote_currency = currency(SYMBOL_CURRENCY_PROFIT);
}

Instrument::Instrument(const Instrument& other)
{
    this.operator=(other);
}

Tick Instrument::tick() const
{
    Tick last_tick;

    Tick::current(m_symbol, last_tick);

    return last_tick;
}

double Instrument::bid() const
{
    return tick().bid();
}

double Instrument::ask() const
{
    return tick().ask();
}

bool Instrument::convert_bid(string currency, double& dest) const
{
    return convert_price(currency, bid(), dest);
}

bool Instrument::convert_ask(string currency, double& dest) const
{
    return convert_price(currency, ask(), dest);
}

bool Instrument::convert_price(string currency, double price, double& dest) const
{
    if (price == 0)
    {
        dest = 0;
        return true;
    }

    if (currency == quote_currency())
    {
        dest = price;
        return true;
    }

    if (currency == base_currency())
    {
        dest = 1 / price;
        return true;
    }

    return false;
}

string Instrument::currency(int type) const
{
    string currency_name;

    if (!SymbolInfoString(m_symbol, type, currency_name))
        return NULL;

    return currency_name;
}

string Instrument::base_currency() const
{
    return m_base_currency;
}

string Instrument::quote_currency() const
{
    return m_quote_currency;
}

bool Instrument::is_forex() const
{
    const string base = base_currency();
    
    if (base == NULL)
        return false;

    const string quote = quote_currency();

    if (quote == NULL)
        return false;

    return base != quote;
}

Instrument* Instrument::operator=(const Instrument& other)
{
    m_symbol         = other.m_symbol;
    m_base_currency  = other.m_base_currency;
    m_quote_currency = other.m_quote_currency;

    return GetPointer(this);
}
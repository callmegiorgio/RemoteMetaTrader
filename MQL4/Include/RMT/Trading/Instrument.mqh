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

    string symbol() const;
    string description() const;
    string base_currency() const;
    string quote_currency() const;
    string margin_currency() const;
    int decimal_places() const;
    double point() const;
    double tick_size() const;
    double contract_size() const;
    double lot_step() const;
    double min_lot() const;
    double max_lot() const;
    int stop_level() const;
    int freeze_level() const;
    int spread() const;

    bool is_complete() const;
    bool is_floating_spread() const;
    bool is_forex() const;

    Instrument* operator=(const Instrument& other);

private:
    bool convert_price(string currency, double price, double& dest) const;

    bool get_property_boolean(ENUM_SYMBOL_INFO_INTEGER type);
    int  get_property_integer(ENUM_SYMBOL_INFO_INTEGER type);
    double get_property_double(ENUM_SYMBOL_INFO_DOUBLE type);
    string get_property_string(ENUM_SYMBOL_INFO_STRING type);

    string m_symbol;
    string m_description;
    string m_base_currency;
    string m_quote_currency;
    string m_margin_currency;
    int    m_decimal_places;
    double m_point;
    double m_tick_size;
    double m_contract_size;
    double m_lot_step;
    double m_min_lot;
    double m_max_lot;
    int    m_stop_level;
    int    m_freeze_level;
    int    m_spread;

    bool m_is_complete;
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
    m_is_complete     = true;
    m_symbol          = symbol;
    m_description     = get_property_string(SYMBOL_DESCRIPTION);
    m_base_currency   = get_property_string(SYMBOL_CURRENCY_BASE);
    m_quote_currency  = get_property_string(SYMBOL_CURRENCY_PROFIT);
    m_margin_currency = get_property_string(SYMBOL_CURRENCY_MARGIN);
    m_decimal_places  = get_property_integer(SYMBOL_DIGITS);
    m_point           = get_property_double(SYMBOL_POINT);
    m_tick_size       = get_property_double(SYMBOL_TRADE_TICK_SIZE);
    m_contract_size   = get_property_double(SYMBOL_TRADE_CONTRACT_SIZE);
    m_lot_step        = get_property_double(SYMBOL_VOLUME_STEP);
    m_min_lot         = get_property_double(SYMBOL_VOLUME_MIN);
    m_max_lot         = get_property_double(SYMBOL_VOLUME_MAX);
    m_stop_level      = get_property_integer(SYMBOL_TRADE_STOPS_LEVEL);
    m_freeze_level    = get_property_integer(SYMBOL_TRADE_FREEZE_LEVEL);
    m_spread          = get_property_boolean(SYMBOL_SPREAD_FLOAT) ? 0 : get_property_integer(SYMBOL_SPREAD);
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

bool Instrument::get_property_boolean(ENUM_SYMBOL_INFO_INTEGER type)
{
    return bool(get_property_integer(type));
}

int Instrument::get_property_integer(ENUM_SYMBOL_INFO_INTEGER type)
{
    long i;

    if (!SymbolInfoInteger(m_symbol, type, i))
    {
        m_is_complete = false;
        return NULL;
    }

    return int(i);
}

double Instrument::get_property_double(ENUM_SYMBOL_INFO_DOUBLE type)
{
    double d;

    if (!SymbolInfoDouble(m_symbol, type, d))
    {
        m_is_complete = false;
        return NULL;
    }

    return d;
}

string Instrument::get_property_string(ENUM_SYMBOL_INFO_STRING type)
{
    string s;

    if (!SymbolInfoString(m_symbol, type, s))
    {
        m_is_complete = false;
        return NULL;
    }

    return s;
}

string Instrument::symbol() const
{
    return m_symbol;
}

string Instrument::description() const
{
    return m_description;
}

string Instrument::base_currency() const
{
    return m_base_currency;
}

string Instrument::quote_currency() const
{
    return m_quote_currency;
}

string Instrument::margin_currency() const
{
    return m_margin_currency;
}

int Instrument::decimal_places() const
{
    return m_decimal_places;
}

double Instrument::point() const
{
    return m_point;
}

double Instrument::tick_size() const
{
    return m_tick_size;
}

double Instrument::contract_size() const
{
    return m_contract_size;
}

double Instrument::lot_step() const
{
    return m_lot_step;
}

double Instrument::min_lot() const
{
    return m_min_lot;
}

double Instrument::max_lot() const
{
    return m_max_lot;
}

int Instrument::stop_level() const
{
    return m_stop_level;
}

int Instrument::freeze_level() const
{
    return m_freeze_level;
}

int Instrument::spread() const
{
    return m_spread;
}

bool Instrument::is_complete() const
{
    return m_is_complete;
}

bool Instrument::is_floating_spread() const
{
    return m_spread == 0;
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
    m_is_complete     = other.m_is_complete;
    m_symbol          = other.m_symbol;
    m_description     = other.m_description;
    m_base_currency   = other.m_base_currency;
    m_quote_currency  = other.m_quote_currency;
    m_margin_currency = other.m_margin_currency;
    m_decimal_places  = other.m_decimal_places;
    m_point           = other.m_point;
    m_tick_size       = other.m_tick_size;
    m_contract_size   = other.m_contract_size;
    m_lot_step        = other.m_lot_step;
    m_min_lot         = other.m_min_lot;
    m_max_lot         = other.m_max_lot;
    m_stop_level      = other.m_stop_level;
    m_freeze_level    = other.m_freeze_level;
    m_spread          = other.m_spread;

    return GetPointer(this);
}
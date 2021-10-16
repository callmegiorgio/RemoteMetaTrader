#property strict

// Local
#include "Instrument.mqh"

/// Retrieves the exchange rate of two currencies.
bool get_exchange_rate(string base_currency, string quote_currency, double& rate)
{
    if (base_currency == quote_currency)
    {
        rate = 1;
        return true;
    }

    OptionalComplex<Instrument> fx_instrument;

    double source_and_target_rate = 0;

    if (find_forex_instrument(fx_instrument, base_currency, quote_currency))
        return fx_instrument.value().convert_bid(quote_currency, rate);
    
    // If we failed to retrieve a pair with the given currencies, try using USD
    // as an intermediary. Example: EURJPY => EURUSD * USDJPY
    const bool should_try_usd_conversion = (base_currency != "USD" && quote_currency != "USD");

    if (!should_try_usd_conversion)
        return false;

    OptionalComplex<Instrument> base_currency_and_usd;

    if (!find_forex_instrument(base_currency_and_usd, base_currency, "USD"))
        return false;

    double base_currency_to_usd_rate = 0;

    if (!base_currency_and_usd.value().convert_bid("USD", base_currency_to_usd_rate))
        return false;

    OptionalComplex<Instrument> quote_currency_and_usd;
    
    if (!find_forex_instrument(quote_currency_and_usd, quote_currency, "USD"))
        return false;
    
    double usd_to_quote_currency_rate = 0;

    if (!quote_currency_and_usd.value().convert_bid(quote_currency, usd_to_quote_currency_rate))
        return false;
    
    rate = base_currency_to_usd_rate * usd_to_quote_currency_rate;
    return true;
}
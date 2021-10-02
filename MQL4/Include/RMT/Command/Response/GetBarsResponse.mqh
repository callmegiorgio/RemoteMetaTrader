#property strict

// Local
#include "../../Utility/JsonValue.mqh"

/// Response:
/// [
///   [datetime, double, double, double, double],
///   [datetime, double, double, double, double],
///   ...
/// ]
class GetBarsResponse {
public:
    void serialize(JsonValue& content)
    {
        for (int i = 0; i < this.rates_count; i++)
        {
            JsonValue* bar = content[i];

            bar[0] = this.rates[i].time;
            bar[1] = this.rates[i].open;
            bar[2] = this.rates[i].high;
            bar[3] = this.rates[i].low;
            bar[4] = this.rates[i].close;
        }
    }

    MqlRates rates[];
    int rates_count;
};
#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// [
///   [datetime, double, double, double, double],
///   [datetime, double, double, double, double],
///   ...
/// ]
class GetBarsResponse {
public:
    void write(JsonWriter& writer) const
    {
        for (int i = 0; i < this.rates_count; i++)
        {
            JsonWriter bar = writer.subdocument(i);

            bar.write(0, this.rates[i].time);
            bar.write(1, this.rates[i].open);
            bar.write(2, this.rates[i].high);
            bar.write(3, this.rates[i].low);
            bar.write(4, this.rates[i].close);
        }
    }

    MqlRates rates[];
    int rates_count;
};
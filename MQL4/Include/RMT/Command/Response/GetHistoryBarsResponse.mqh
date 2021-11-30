#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// [
///   [string, double, double, double, double, integer],
///   [string, double, double, double, double, integer],
///   ...
/// ]
class GetHistoryBarsResponse {
public:
    void write(JsonWriter& writer) const
    {
        for (int i = 0; i < this.rates_count; i++)
        {
            JsonWriter bar = writer.subdocument(i);

            bar.write(0, TimeToStr(this.rates[i].time, TIME_DATE|TIME_SECONDS));
            bar.write(1, this.rates[i].open);
            bar.write(2, this.rates[i].high);
            bar.write(3, this.rates[i].low);
            bar.write(4, this.rates[i].close);
            bar.write(5, this.rates[i].tick_volume);
        }
    }

    MqlRates rates[];
    int rates_count;
};
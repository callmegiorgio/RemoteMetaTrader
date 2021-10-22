#property strict

// Local
#include "../../Trading/Bar.mqh"
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// [datetime, double, double, double, double, integer]
class GetBarResponse {
public:
    void write(JsonWriter& writer) const
    {
        writer.write(0, this.bar.time());
        writer.write(1, this.bar.open());
        writer.write(2, this.bar.high());
        writer.write(3, this.bar.low());
        writer.write(4, this.bar.close());
        writer.write(5, this.bar.volume());
    }

    Bar bar;
};
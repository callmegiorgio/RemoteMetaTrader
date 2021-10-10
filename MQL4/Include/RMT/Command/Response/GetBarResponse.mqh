#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// [datetime, double, double, double, double, integer]
class GetBarResponse {
public:
    void write(JsonWriter& writer) const
    {
        writer.write(0, this.time);
        writer.write(1, this.open);
        writer.write(2, this.high);
        writer.write(3, this.low);
        writer.write(4, this.close);
        writer.write(5, this.volume);
    }

    datetime time;
    double   open;
    double   high;
    double   low;
    double   close;
    long     volume;
};
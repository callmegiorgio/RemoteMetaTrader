#property strict

// Local
#include "../../Trading/Tick.mqh"
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// {
///   "time": string,
///   "bid":  double,
///   "ask":  double
/// }
class GetTickResponse {
public:
    void write(JsonWriter& writer) const
    {
        writer.write("time", TimeToStr(this.last_tick.server_time(), TIME_DATE|TIME_SECONDS));
        writer.write("bid",  this.last_tick.bid());
        writer.write("ask",  this.last_tick.ask());
    }

    Tick last_tick;
};
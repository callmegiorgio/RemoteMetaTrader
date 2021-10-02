#property strict

// Local
#include "../../Trading/Tick.mqh"
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// {
///   "time": datetime,
///   "bid":  double,
///   "ask":  double
/// }
class GetTickResponse {
public:
    void write(JsonWriter& writer) const
    {
        writer.write("time", this.last_tick.server_time());
        writer.write("bid",  this.last_tick.bid());
        writer.write("ask",  this.last_tick.ask());
    }

    Tick last_tick;
};
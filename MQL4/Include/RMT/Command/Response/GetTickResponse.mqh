#property strict

// Local
#include "../../Trading/Tick.mqh"
#include "../../Utility/JsonValue.mqh"

/// Response:
/// {
///   "time": datetime,
///   "bid":  double,
///   "ask":  double
/// }
class GetTickResponse {
public:
    void serialize(JsonValue& content)
    {
        content["time"] = this.last_tick.server_time();
        content["bid"]  = this.last_tick.bid();
        content["ask"]  = this.last_tick.ask();
    }

    Tick last_tick;
};
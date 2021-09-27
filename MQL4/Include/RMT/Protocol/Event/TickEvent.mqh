#property strict

// Local
#include "../../Trading/Tick.mqh"

/// Name: tick.<symbol>
/// Body: [datetime, float, float]
class TickEvent {
public:
    string name() const
    {
        return "tick:" + symbol;
    }

    bool write(JsonValue& msg) const
    {
        msg[0] = this.tick.server_time();
        msg[1] = this.tick.bid();
        msg[2] = this.tick.ask();

        return true;
    }

    string symbol;
    Tick   tick;
};
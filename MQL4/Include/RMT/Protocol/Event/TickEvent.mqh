#property strict

// Local
#include "../../Network/Event.mqh"
#include "../../Trading/Tick.mqh"
#include "../../Utility/JsonValue.mqh"

/// Name: tick.<symbol>
/// Body: [datetime, float, float]
class TickEvent : public Event {
public:
    string name() const override
    {
        return "tick:" + symbol;
    }

    string body() const override
    {
        JsonValue msg;

        msg[0] = this.tick.server_time();
        msg[1] = this.tick.bid();
        msg[2] = this.tick.ask();

        return msg.serialize();
    }

    string symbol;
    Tick   tick;
};
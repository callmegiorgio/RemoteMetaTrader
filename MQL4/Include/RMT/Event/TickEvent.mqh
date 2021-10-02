#property strict

// Local
#include "../Trading/Tick.mqh"
#include "Event.mqh"

/// Name: tick.<symbol>
/// Content: [datetime, float, float]
class TickEvent : public Event {
public:
    string name() const override
    {
        return "tick." + symbol;
    }

    JsonValue content() const override
    {
        JsonValue msg;

        msg[0] = this.tick.server_time();
        msg[1] = this.tick.bid();
        msg[2] = this.tick.ask();

        return msg;
    }

    string symbol;
    Tick   tick;
};
#property strict

/// {
///   "evt": "tick"
///   "msg": [string, datetime, float, float]
/// }

class TickEvent {
public:
    static string name() { return "tick"; }

    bool write(JsonValue& message) const
    {
        message[0] = this.symbol;
        message[1] = this.tick.time;
        message[2] = this.tick.bid;
        message[3] = this.tick.ask;
        return true;
    }

    string symbol;
    MqlTick tick;
};
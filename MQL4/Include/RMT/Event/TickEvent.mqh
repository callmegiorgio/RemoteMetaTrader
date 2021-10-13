#property strict

// Local
#include "../Trading/Tick.mqh"

/// Event notified when an instrument receives a new tick.
class TickEvent {
public:
    string symbol;
    Tick   tick;
};
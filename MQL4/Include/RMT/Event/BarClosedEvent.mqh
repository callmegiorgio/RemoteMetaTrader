#property strict

// Local
#include "../Trading/Bar.mqh"

/// Event notified when an instrument's M1 bar is closed.
class BarClosedEvent {
public:
    string symbol;
    Bar    bar;
};
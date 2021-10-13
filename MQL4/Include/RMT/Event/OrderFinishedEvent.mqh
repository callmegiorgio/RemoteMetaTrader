#property strict

// Local
#include "../Trading/Order.mqh"

/// Event notified when an order is closed, canceled, or expired.
class OrderFinishedEvent {
public:
    int    ticket;
    Order* order;
};
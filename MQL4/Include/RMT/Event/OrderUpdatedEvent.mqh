#property strict

// Local
#include "../Trading/Order.mqh"

/// Event notified when an order's comment, commission, profit, or swap changes.
class OrderUpdatedEvent {
public:
    int    ticket;
    Order* order;
};
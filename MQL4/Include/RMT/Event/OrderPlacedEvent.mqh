#property strict

// Local
#include "../Trading/Order.mqh"

/// Event notified when a new order is opened or filled, or a pending order is filled.
class OrderPlacedEvent {
public:
    int    ticket;
    Order* order;
};
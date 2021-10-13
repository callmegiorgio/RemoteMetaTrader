#property strict

// Local
#include "../Trading/Order.mqh"

/// Event notified when an order is modified by `OrderModify()`.
class OrderModifiedEvent {
public:
    int    ticket;
    Order* order;
};
#property strict

// Local
#include "../Network/Server.mqh"
#include "../Trading/Order.mqh"
#include "../Utility/JsonValue.mqh"
#include "../Utility/Observer.mqh"
#include "OrderUpdatedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Publishes `OrderUpdatedEvent` messages of the following layout:
///
/// Event name: "orderUpdated"
/// Event content:
/// {
///    "ticket":     integer,
///    "comment":    string,
///    "commission": double,
///    "profit":     double,
///    "swap":       double
/// }
///
////////////////////////////////////////////////////////////////////////////////
class OrderUpdatedEventPublisher : public Observer<OrderUpdatedEvent> {
public:
    OrderUpdatedEventPublisher(Server& the_server)
    {
        m_server = GetPointer(the_server);
    }

    void on_notify(const OrderUpdatedEvent& event) override
    {
        JsonValue msg;

        msg["ticket"]     = event.ticket;
        msg["comment"]    = event.order.comment;
        msg["commission"] = event.order.commission;
        msg["profit"]     = event.order.profit;
        msg["swap"]       = event.order.swap;

        m_server.publish("orderUpdated", msg.serialize());
    }

private:
    Server* m_server;
};
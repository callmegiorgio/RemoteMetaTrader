#property strict

// Local
#include "../Network/Server.mqh"
#include "../Trading/Order.mqh"
#include "../Utility/JsonValue.mqh"
#include "../Utility/Observer.mqh"
#include "OrderModifiedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Publishes `OrderModifiedEvent` messages of the following layout:
///
/// Event name: "orderModified"
/// Event content:
/// {
///    "ticket":     integer,
///    "op":         double,
///    "sl":         double,
///    "tp":         double,
///    "expiration": datetime
/// }
///
////////////////////////////////////////////////////////////////////////////////
class OrderModifiedEventPublisher : public Observer<OrderModifiedEvent> {
public:
    OrderModifiedEventPublisher(Server& the_server)
    {
        m_server = GetPointer(the_server);
    }

    void on_notify(const OrderModifiedEvent& event) override
    {
        JsonValue msg;

        msg["ticket"]     = event.ticket;
        msg["op"]         = event.order.open_price;
        msg["sl"]         = event.order.stop_loss;
        msg["tp"]         = event.order.take_profit;
        msg["expiration"] = event.order.expiration;

        m_server.publish("orderModified" + " " + msg.serialize());
    }

private:
    Server* m_server;
};
#property strict

// Local
#include "../Network/Server.mqh"
#include "../Trading/Order.mqh"
#include "../Utility/JsonValue.mqh"
#include "../Utility/Observer.mqh"
#include "OrderFinishedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Publishes `OrderFinishedEvent` messages of the following layout:
///
/// Event name: "orderFinished"
/// Event content:
/// {
///    "ticket":     integer,
///    "opcode":     integer,
///    "cp":         double,
///    "ct":         datetime,
///    "sl":         double,
///    "tp":         double,
///    "expiration": datetime,
///    "comment":    string,
///    "commission": double,
///    "profit":     double,
///    "swap":       double
/// }
///
////////////////////////////////////////////////////////////////////////////////
class OrderFinishedEventPublisher : public Observer<OrderFinishedEvent> {
public:
    OrderFinishedEventPublisher(Server& the_server)
    {
        m_server = GetPointer(the_server);
    }

    void on_notify(const OrderFinishedEvent& event) override
    {
        JsonValue msg;

        msg["ticket"]     = event.ticket;
        msg["opcode"]     = event.order.type;
        msg["cp"]         = event.order.close_price;
        msg["ct"]         = event.order.close_time;
        msg["sl"]         = event.order.stop_loss;
        msg["tp"]         = event.order.take_profit;
        msg["expiration"] = event.order.expiration;
        msg["comment"]    = event.order.comment;
        msg["commission"] = event.order.commission;
        msg["profit"]     = event.order.profit;
        msg["swap"]       = event.order.swap;

        m_server.publish("orderFinished", msg.serialize());
    }

private:
    Server* m_server;
};
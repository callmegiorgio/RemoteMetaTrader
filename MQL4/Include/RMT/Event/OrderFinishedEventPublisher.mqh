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
///    "sl":         ?double,
///    "tp":         ?double,
///    "expiration": ?datetime,
///    "comment":    ?string,
///    "commission": ?double,
///    "profit":     ?double,
///    "swap":       ?double
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

        msg["ticket"] = event.ticket;
        msg["opcode"] = event.order.type;
        msg["cp"]     = event.order.close_price;
        msg["ct"]     = event.order.close_time;

        if (event.order.stop_loss != 0)
            msg["sl"] = event.order.stop_loss;

        if (event.order.take_profit != 0)
            msg["tp"] = event.order.take_profit;

        if (event.order.expiration != 0)
            msg["expiration"] = event.order.expiration;

        if (event.order.comment != NULL && event.order.comment != "")
            msg["comment"] = event.order.comment;

        if (event.order.commission != 0)
            msg["commission"] = event.order.commission;

        if (event.order.profit != 0)
            msg["profit"] = event.order.profit;

        if (event.order.swap != 0)
            msg["swap"] = event.order.swap;

        m_server.publish("orderFinished", msg.serialize());
    }

private:
    Server* m_server;
};
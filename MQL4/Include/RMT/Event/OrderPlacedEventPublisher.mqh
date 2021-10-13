#property strict

// Local
#include "../Network/Server.mqh"
#include "../Trading/Order.mqh"
#include "../Utility/JsonValue.mqh"
#include "../Utility/Observer.mqh"
#include "OrderPlacedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Publishes `OrderPlacedEvent` messages of the following layout:
///
/// Event name: "orderPlaced"
/// Event content:
/// {
///    "ticket":     integer,
///    "symbol":     string,
///    "lots":       double,
///    "opcode":     integer,
///    "op":         double,
///    "ot":         datetime,
///    "sl":         double,
///    "tp":         double,
///    "expiration": datetime,
///    "magic":      integer,
///    "comment":    string,
///    "commission": double,
///    "profit":     double,
///    "swap":       double
/// }
///
////////////////////////////////////////////////////////////////////////////////
class OrderPlacedEventPublisher : public Observer<OrderPlacedEvent> {
public:
    OrderPlacedEventPublisher(Server& the_server)
    {
        m_server = GetPointer(the_server);
    }

    void on_notify(const OrderPlacedEvent& event) override
    {
        JsonValue msg;

        msg["ticket"]     = event.ticket;
        msg["symbol"]     = event.order.symbol;
        msg["lots"]       = event.order.lots;
        msg["opcode"]     = event.order.type;
        msg["op"]         = event.order.open_price;
        msg["ot"]         = event.order.open_time;
        msg["sl"]         = event.order.stop_loss;
        msg["tp"]         = event.order.take_profit;
        msg["expiration"] = event.order.expiration;
        msg["magic"]      = event.order.magic_number;
        msg["comment"]    = event.order.comment;
        msg["commission"] = event.order.commission;
        msg["profit"]     = event.order.profit;
        msg["swap"]       = event.order.swap;

        m_server.publish("orderPlaced", msg.serialize());
    }

private:
    Server* m_server;
};
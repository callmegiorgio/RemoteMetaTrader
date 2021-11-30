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
///    "sl":         ?double,
///    "tp":         ?double,
///    "expiration": ?datetime,
///    "magic":      ?integer,
///    "comment":    ?string,
///    "commission": ?double,
///    "profit":     ?double,
///    "swap":       ?double
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
        msg["ot"]         = TimeToStr(event.order.open_time, TIME_DATE|TIME_SECONDS);

        if (event.order.stop_loss != 0)
            msg["sl"] = event.order.stop_loss;

        if (event.order.take_profit != 0)
            msg["tp"] = event.order.take_profit;

        if (event.order.expiration != 0)
            msg["expiration"] = TimeToStr(event.order.expiration, TIME_DATE|TIME_SECONDS);

        if (event.order.magic_number != 0)
            msg["magic"] = event.order.magic_number;

        if (event.order.comment != NULL && event.order.comment != "")
            msg["comment"] = event.order.comment;

        if (event.order.commission != 0)
            msg["commission"] = event.order.commission;

        if (event.order.profit != 0)
            msg["profit"] = event.order.profit;

        if (event.order.swap != 0)
            msg["swap"] = event.order.swap;

        m_server.publish("orderPlaced", msg.serialize());
    }

private:
    Server* m_server;
};
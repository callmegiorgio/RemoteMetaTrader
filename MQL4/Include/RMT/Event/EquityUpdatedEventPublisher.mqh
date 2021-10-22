#property strict

// Local
#include "../Network/Server.mqh"
#include "../Utility/JsonValue.mqh"
#include "../Utility/Observer.mqh"
#include "EquityUpdatedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Publishes `EquityUpdatedEvent` messages of the following layout:
///
/// Event name: "equityUpdated"
/// Event content:
/// {
///   "equity":     double,
///   "profit":     double,
///   "margin":     double,
///   "marginLvl":  double,
///   "freeMargin": double,
///   "balance":    ?double
/// }
///
////////////////////////////////////////////////////////////////////////////////
class EquityUpdatedEventPublisher : public Observer<EquityUpdatedEvent> {
public:
    EquityUpdatedEventPublisher(Server& the_server)
    {
        m_server = GetPointer(the_server);
    }
    
    void on_notify(const EquityUpdatedEvent& event) override
    {
        JsonValue msg;

        msg["equity"]     = event.equity;
        msg["profit"]     = event.profit;
        msg["margin"]     = event.margin;
        msg["marginLvl"]  = event.margin_level;
        msg["freeMargin"] = event.free_margin;

        if (event.balance.has_value())
            msg["balance"] = event.balance.value();

        m_server.publish("equityUpdated", msg.serialize());
    }

private:
    Server* m_server;
};
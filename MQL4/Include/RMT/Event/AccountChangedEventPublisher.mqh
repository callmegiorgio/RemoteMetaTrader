#property strict

// Local
#include "../Network/Server.mqh"
#include "../Utility/JsonValue.mqh"
#include "../Utility/Observer.mqh"
#include "AccountChangedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Publishes `AccountChangedEvent` messages of the following layout:
///
/// Event name: "accountChanged"
/// Event content:
/// {
///   "currency":        string,
///   "leverage":        integer
///   "credit":          double,
///   "expertAllowed":   bool,
///   "tradeAllowed":    bool,
///   "maxActiveOrders": integer
/// }
///
////////////////////////////////////////////////////////////////////////////////
class AccountChangedEventPublisher : public Observer<AccountChangedEvent> {
public:
    AccountChangedEventPublisher(Server& the_server)
    {
        m_server = GetPointer(the_server);
    }
    
    void on_notify(const AccountChangedEvent& event) override
    {
        JsonValue msg;

        msg["currency"]        = event.currency;
        msg["leverage"]        = event.leverage;
        msg["credit"]          = event.credit;
        msg["expertAllowed"]   = event.expert_allowed;
        msg["tradeAllowed"]    = event.trade_allowed;
        msg["maxActiveOrders"] = event.max_active_orders;

        m_server.publish("accountChanged", msg.serialize());
    }

private:
    Server* m_server;
};
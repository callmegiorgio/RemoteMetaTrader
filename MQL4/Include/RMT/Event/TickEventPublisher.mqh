#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "../Network/Server.mqh"
#include "../Trading/Tick.mqh"
#include "../Utility/JsonValue.mqh"
#include "../Utility/Observer.mqh"
#include "TickEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Publishes `TickEvent` messages of the following layout:
///
/// Event static name: "tick"
/// Event dynamic name: instrument symbol
/// Event content:
/// [
///    datetime,
///    double,
///    double
/// ]
///
////////////////////////////////////////////////////////////////////////////////
class TickEventPublisher : public Observer<TickEvent> {
public:
    TickEventPublisher(Server& the_server)
    {
        m_server = GetPointer(the_server);
    }
    
    void on_notify(const TickEvent& event) override
    {
        JsonValue msg;

        msg[0] = event.tick.server_time();
        msg[1] = event.tick.bid();
        msg[2] = event.tick.ask();

        m_server.publish("tick." + event.symbol + " " + msg.serialize());
    }

private:
    Server* m_server;
};
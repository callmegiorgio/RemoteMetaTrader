#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "../Network/Server.mqh"
#include "../Trading/Bar.mqh"
#include "../Utility/JsonValue.mqh"
#include "../Utility/Observer.mqh"
#include "BarClosedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Publishes `BarClosedEvent` messages of the following layout:
///
/// Event static name: "bar"
/// Event dynamic name: instrument symbol
/// Event content:
/// {
///    "time": datetime,
///    "open": double,
///    "high": double,
///    "low": double,
///    "close": double,
///    "volume": integer
/// }
///
////////////////////////////////////////////////////////////////////////////////
class BarClosedEventPublisher : public Observer<BarClosedEvent> {
public:
    BarClosedEventPublisher(Server& the_server)
    {
        m_server = GetPointer(the_server);
    }
    
    void on_notify(const BarClosedEvent& event) override
    {
        JsonValue msg;

        msg["time"]   = event.bar.time();
        msg["open"]   = event.bar.open();
        msg["high"]   = event.bar.high();
        msg["low"]    = event.bar.low();
        msg["close"]  = event.bar.close();
        msg["volume"] = event.bar.volume();

        m_server.publish("bar." + event.symbol, msg.serialize());
    }

private:
    Server* m_server;
};
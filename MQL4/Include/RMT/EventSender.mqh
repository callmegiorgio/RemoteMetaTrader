#property strict

// Local
#include "Server.mqh"

class EventSender {
public:
    EventSender(Server& the_server);

    template <typename T>
    bool notify(const T& event);

private:
    Server* m_server;
};

//===========================================================================
// --- EventSender implementation ---
//===========================================================================
EventSender::EventSender(Server& the_server)
{
    m_server = GetPointer(the_server);
}

template <typename T>
bool EventSender::notify(const T& event)
{
    JsonValue root;
    JsonValue* content = root["msg"];

    if (!content)
        return false;

    if (!event.write(*content))
        return false;
    
    root["evt"] = event.name();
    
    return m_server.send_event(root.serialize());
}
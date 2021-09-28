#property strict

// Local
#include "Event.mqh"
#include "Server.mqh"

class EventPublisher {
public:
    EventPublisher(Server& the_server);

    void publish(const Event& event);

    virtual void process_events() = 0;

private:
    Server* m_server;
};

//===========================================================================
// --- EventSender implementation ---
//===========================================================================
EventPublisher::EventPublisher(Server& the_server)
{
    m_server = GetPointer(the_server);
}

void EventPublisher::publish(const Event& event)
{
    const string msg_name = event.name();

    if (msg_name == "")
    {
        Print("Missing event name");
        return;
    }

    m_server.publish_event(StringFormat("%s %s", msg_name, event.body()));
}
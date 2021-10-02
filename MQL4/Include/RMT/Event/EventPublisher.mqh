#property strict

// Local
#include "../Network/Server.mqh"
#include "Event.mqh"

class EventPublisher {
public:
    EventPublisher(Server& the_server);

    void publish(const Event& event);

    virtual void process_events() = 0;

private:
    Server* m_server;
};

//===========================================================================
// --- EventPublisher implementation ---
//===========================================================================
EventPublisher::EventPublisher(Server& the_server)
{
    m_server = GetPointer(the_server);
}

void EventPublisher::publish(const Event& event)
{
    const string event_name = event.name();

    if (event_name == "")
    {
        Print("Missing event name");
        return;
    }

    JsonValue content = event.content();

    if (content.type() != JSON_OBJECT && content.type() != JSON_ARRAY)
    {
        PrintFormat("error: event '%s' is neither a JSON object nor a JSON array", event_name);
        return;
    }

    const string content_str = content.serialize();

    if (content_str == NULL || content_str == "")
    {
        PrintFormat("serialization of event '%s' failed", event_name);
        return;
    }

    m_server.publish_event(StringFormat("%s %s", event_name, content_str));
}
#property strict

// Local
#include "Server.mqh"

class EventPublisher {
public:
    EventPublisher(Server& the_server);

    template <typename T>
    bool publish(const T& event);

private:
    void on_missing_name_error()
    {
        Print("Missing event name");
    }

    void on_writing_failed(string name)
    {
        Print("Failed to write body of event '", name, "'");
    }

    Server* m_server;
};

//===========================================================================
// --- EventSender implementation ---
//===========================================================================
EventPublisher::EventPublisher(Server& the_server)
{
    m_server = GetPointer(the_server);
}

template <typename T>
bool EventPublisher::publish(const T& event)
{
    const string msg_name = event.name();

    if (msg_name == "")
    {
        on_missing_name_error();
        return false;
    }

    JsonValue msg_body;

    if (!event.write(msg_body))
    {
        on_writing_failed(msg_name);
        return false;
    }
    
    return m_server.publish_event(msg_name + " " + msg_body.serialize());
}
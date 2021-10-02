#property strict

#include "../Include/RMT/Command/RequestProcessor.mqh"
#include "../Include/RMT/Event/TickEventPublisher.mqh"
#include "../Include/RMT/Network/Server.mqh"

extern string PROJECT_NAME      = "__RMT_Exp3rt_;D__";
extern string PROTOCOL          = "tcp";
extern string HOSTNAME          = "*";
extern int    REP_PORT          = 32768;
extern int    PUB_PORT          = 32769;
extern int    MILLISECOND_TIMER = 100;

Server             server(PROJECT_NAME);
TickEventPublisher tick_event_publisher(server);
RequestProcessor   request_processor(server, tick_event_publisher);

int OnInit()
{
    if (!server.run(PROTOCOL, HOSTNAME, REP_PORT, PUB_PORT))
        return INIT_FAILED;

    // `OnTimer()` is not called while testing.
    if (!IsTesting())
        EventSetMillisecondTimer(MILLISECOND_TIMER);

    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
    server.stop();

    if (!IsTesting())
        EventKillTimer();
}

void OnTick()
{
    request_processor.process_requests();
    tick_event_publisher.process_events();
}

void OnTimer()
{
    request_processor.process_requests();
    tick_event_publisher.process_events();
}
#property strict

#include "../Include/RMT/Server.mqh"
#include "../Include/RMT/RequestProcessor.mqh"
#include "../Include/RMT/TickEventWatcher.mqh"

extern string PROJECT_NAME      = "__RMT_Exp3rt_;D__";
extern string PROTOCOL          = "tcp";
extern string HOSTNAME          = "*";
extern int    REP_PORT          = 32768;
extern int    PUB_PORT          = 32769;
extern int    MILLISECOND_TIMER = 100;

Server           server(PROJECT_NAME);
TickEventWatcher tick_event_watcher(server);
RequestProcessor request_processor(server, tick_event_watcher);

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
    request_processor.process();
    tick_event_watcher.process_events();
}

void OnTimer()
{
    request_processor.process();
    tick_event_watcher.process_events();
}
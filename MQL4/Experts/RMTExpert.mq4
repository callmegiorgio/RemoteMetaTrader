#property strict

#include "../Include/RMT/Server.mqh"
#include "../Include/RMT/RequestProcessor.mqh"
#include "../Include/RMT/TickEventWatcher.mqh"

extern string PROJECT_NAME      = "__RMT_Exp3rt_;D__";
extern string PROTOCOL          = "tcp";
extern string HOSTNAME          = "*";
extern int    REP_PORT          = 32768;
extern int    PUSH_PORT         = 32769;
extern int    MILLISECOND_TIMER = 100;

Server           server(PROJECT_NAME);
TickEventWatcher tick_event_watcher(server);
RequestProcessor request_processor(server, tick_event_watcher);

int OnInit()
{
    // `OnTimer()` is not called while testing.
    if (!IsTesting())
        EventSetMillisecondTimer(MILLISECOND_TIMER);

    if (!server.run(PROTOCOL, HOSTNAME, REP_PORT, PUSH_PORT))
        return INIT_FAILED;

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
    tick_event_watcher.notify_events();
}

void OnTimer()
{
    request_processor.process();
    tick_event_watcher.notify_events();
}
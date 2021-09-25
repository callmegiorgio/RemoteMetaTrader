#property strict

#include "../Include/RMT/Server.mqh"
#include "../Include/RMT/RequestProcessor.mqh"
#include "../Include/RMT/SymbolWatcher.mqh"

extern string PROJECT_NAME      = "__RMT_Exp3rt_;D__";
extern string PROTOCOL          = "tcp";
extern string HOSTNAME          = "*";
extern int    REP_PORT          = 32768;
extern int    PUSH_PORT         = 32769;
extern int    MILLISECOND_TIMER = 100;

Server server(PROJECT_NAME);
RequestProcessor request_processor;

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
    process_request();
    publish_symbols();
}

void OnTimer()
{
    process_request();
    publish_symbols();
}

void process_request()
{
    string request;

    if (!server.recv_request(request))
        return;

    Print("Received request: ", request);

    string response = request_processor.process(request, true);

    if (response == NULL)
    {
        Print("Request parsing failed; no reply");
        server.send_response("");
        return;
    }

    Print("Sending response: ", response);
    server.send_response(response);
}

void publish_symbols()
{
    SymbolTick ticks[];
    const int ticks_count = SymbolWatcher::instance().get_ticks(ticks);
    string messages[];

    if (ArrayResize(messages, ticks_count) != ticks_count)
    {
        Print("Failed to resize ticks array");
        return;
    }
    
    for (int i = 0; i < ticks_count; i++)
    {    
        const string csv_msg =
            StringFormat("%s;%I64u;%f;%f",
                ticks[i].symbol,
                ticks[i].mql_tick.time,
                ticks[i].mql_tick.bid,
                ticks[i].mql_tick.ask
            );

        messages[i] = csv_msg;
    }

    server.send_ticks(messages);
}
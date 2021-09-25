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

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // `OnTimer()` is not called while testing.
    if (!IsTesting())
        EventSetMillisecondTimer(MILLISECOND_TIMER);
    
    Print("binding server to REP socket on port ", REP_PORT, "...");
    Print("binding server to PUSH socket on port ", PUSH_PORT, "...");

    server.run(PROTOCOL, HOSTNAME, REP_PORT, PUSH_PORT);

    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("unbinding server from REP socket on port ", REP_PORT, "...");
    Print("unbinding server from PUSH socket on port ", PUSH_PORT, "...");

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
    const string request = server.read_request();

    if (request == NULL)
        return;

    Print("Received request: ", request);

    string response = request_processor.process(request, true);

    if (response == NULL)
    {
        Print("Request parsing failed; no reply");
        server.send_response("");
        return;
    }

    Print("Sending reply: ", response);

    if (!server.send_response(response))
        Print("Failed to send reply");
}

void publish_symbols()
{
    SymbolTick ticks[];
    const int ticks_count = SymbolWatcher::instance().get_ticks(ticks);
    
    for (int i = 0; i < ticks_count; i++)
    {    
        const string csv_msg =
            StringFormat("%s;%I64u;%f;%f",
                ticks[i].symbol,
                ticks[i].mql_tick.time,
                ticks[i].mql_tick.bid,
                ticks[i].mql_tick.ask
            );
        
        Print("sending tick msg: ", csv_msg);

        server.send_tick(csv_msg);
    }
}
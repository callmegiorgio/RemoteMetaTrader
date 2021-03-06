#property strict

#include "../Include/RMT/Command/RequestProcessor.mqh"
#include "../Include/RMT/Event/TickEventPublisher.mqh"
#include "../Include/RMT/Network/Server.mqh"
#include "../Include/RMT/Utility/sleep.mqh"
#include "../Include/RMT/Utility/Time.mqh"

//==============================================================================
// Input variables.
//==============================================================================
static input string PROTOCOL          = "tcp"; // Protocol on which to bind the REP and PUB sockets.
static input string HOSTNAME          = "*";   // Address on which to bind the REP and PUB sockets.
static input int    REP_PORT          = 32768; // Port on which the REP socket of the REQ-REP topology will bind.
static input int    PUB_PORT          = 32769; // Port on which the PUB socket of the PUB-SUB topology will bind.
static input int    MILLISECOND_TIMER = 100;   // Period in milliseconds between calls to OnTimer().
static input int    START_HOUR        = 0;     // Hour to start processing OnTick() on Strategy Tester.
static input int    START_MINUTE      = 0;     // Minute to start processing OnTick() on Strategy Tester.
static input int    START_SECOND      = 0;     // Second to start processing OnTick() on Strategy Tester.
static input int    STOP_HOUR         = 23;    // Hour to stop processing OnTick() on Strategy Tester.
static input int    STOP_MINUTE       = 59;    // Minute to stop processing OnTick() on Strategy Tester.
static input int    STOP_SECOND       = 59;    // Second to stop processing OnTick() on Strategy Tester.

//==============================================================================
// Global variables.
//==============================================================================
typedef void(*OnTickHandler)(void);

const Time testing_start_time(START_HOUR, START_MINUTE, START_SECOND);
const Time testing_stop_time(STOP_HOUR, STOP_MINUTE, STOP_SECOND);

Server             server;
TickEventPublisher tick_event_publisher(server);
RequestProcessor   request_processor(server, tick_event_publisher);

// Branches out `OnTick()` logic to different functions, depending on whether
// the Expert is run by Strategy Tester or not.
OnTickHandler on_tick_handler;

//==============================================================================
// Expert's logic.
//==============================================================================
int OnInit()
{
    if (!server.run(PROTOCOL, HOSTNAME, REP_PORT, PUB_PORT))
        return INIT_FAILED;

    if (IsTesting())
    {
        on_tick_handler = on_tester_tick;

        PrintFormat(
            "Testing starts at %s and stops at %s",
            testing_start_time.str(),
            testing_stop_time.str()
        );
    }
    else
    {
        on_tick_handler = on_chart_tick;

        // `OnTimer()` is not called while testing.
        EventSetMillisecondTimer(MILLISECOND_TIMER);
    }

    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
    if (!IsTesting())
        EventKillTimer();

    server.stop();
}

void OnTick()
{
    on_tick_handler();
}

void OnTimer()
{
    request_processor.process_requests();
    tick_event_publisher.process_events();
}

/// Called by `OnTick()` if the Expert is being run by Strategy Tester.
void on_tester_tick()
{
    const Time current_time = Time::now();

    // When running the expert on Strategy Tester, the below call to sleep() will slow
    // down the Tester's execution. To speed things up, we can ignore bars that aren't
    // relevant in a strategy by specifying a start and stop time for the Tester.
    if (current_time < testing_start_time)
        return;
    
    if (current_time >= testing_stop_time)
    {
        ExpertRemove();
        return;
    }

    request_processor.process_requests();
    tick_event_publisher.process_events();

    //==============================================================================
    // Synchronize the expert server with clients.
    //
    // After the above call to `tick_event_publisher.process_events()` returns, new
    // tick events may have been sent to clients, which in turn may make clients
    // process them and want to place orders in that tick. So, we force the server
    // to sleep for a while to give clients enough time to receive and process new
    // ticks, and then we process any further client requests.
    //
    // This is required, since `RequestProcessor` is called before event publishers.
    //
    // Here's an example to illustrate this. Say a tick of a trading instrument is
    // 200.16. A client that's interested in such an instrument receives this tick
    // and decides to place an order on it, so ideally, the order should be placed
    // at 200.16 (assuming slippage is zero). However, without the logic below, the
    // processing of the client's order placing request would only be processed on
    // the next call to this function, in which case the instrument's tick wouldn't
    // be 200.16 anymore. Let's say the new tick is 200.18. So, the new order would
    // be placed at 200.18 instead of the desired 200.16.
    //
    // Thus, by calling the `RequestProcessor` another time, we make sure clients
    // will place orders on the latest ticks on Strategy Tester; and by calling
    // `sleep()` before it, we make sure clients will have enough time to receive
    // and process ticks, as otherwise a call to `RequestProcessor` may return
    // prematurely for not having received any requests.
    //
    // None of this is required when the expert is attached to a chart, that is,
    // when it's not run by the Strategy Tester, because `OnTimer()` will be called
    // and requests will be eventually processed.
    //==============================================================================
    sleep(1);
    request_processor.process_requests();
}

/// Called by `OnTick()` if the Expert is being run while attached to a chart.
void on_chart_tick()
{
    request_processor.process_requests();
    tick_event_publisher.process_events();
}
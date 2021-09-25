#property strict

// Local
#include "Protocol/Request/CloseOrderHandler.mqh"
#include "Protocol/Request/GetBarsHandler.mqh"
#include "Protocol/Request/GetTickHandler.mqh"
#include "Protocol/Request/InvalidCommandHandler.mqh"
#include "Protocol/Request/PlaceOrderHandler.mqh"
#include "Protocol/Request/WatchSymbolHandler.mqh"
#include "MessageDispatcher.mqh"
#include "Server.mqh"
#include "TickEventWatcher.mqh"

class RequestProcessor {
public:
    RequestProcessor(Server& the_server, TickEventWatcher& the_tick_watcher);
    
    void process();

private:
    string process(const string& request);

    Server*           m_server;
    MessageDispatcher m_dispatcher;
};

//===========================================================================
// --- RequestProcessor implementation ---
//===========================================================================
RequestProcessor::RequestProcessor(Server& the_server, TickEventWatcher& the_tick_watcher)
{
    m_server = GetPointer(the_server);

    m_dispatcher.set_fallback_handler(new InvalidCommandHandler());
    m_dispatcher.set_handler("watch_symbol", new WatchSymbolHandler(the_tick_watcher));
    m_dispatcher.set_handler("get_tick",     new GetTickHandler());
    m_dispatcher.set_handler("get_bars",     new GetBarsHandler());
    m_dispatcher.set_handler("place_order",  new PlaceOrderHandler());
    m_dispatcher.set_handler("close_order",  new CloseOrderHandler());
}

void RequestProcessor::process()
{
    string request;

    if (!server.recv_request(request))
        return;

    Print("Received request: ", request);

    string response = process(request);

    if (response == NULL)
    {
        Print("Request parsing failed; no reply");
        server.send_response("");
        return;
    }

    Print("Sending response: ", response);
    server.send_response(response);
}

string RequestProcessor::process(const string& request)
{
    const JsonValue json_request = JsonValue::deserialize(request);

    if (!json_request)
    {
        Print("Failed to deserialize request");
        return NULL;
    }
    
    const JsonValue* json_cmd = json_request.find("cmd");

    if (!json_cmd)
    {
        Print("Request is missing key 'cmd'");
        return NULL;
    }

    bool ok;
    const string cmd = json_cmd.to_string(ok);

    if (!ok)
    {
        Print("Invalid type for key 'cmd' (expected string)");
        return NULL;
    }
    
    const JsonValue* request_msg = json_request.find("msg");
    
    if (!request_msg)
    {
        Print("Request is missing key 'msg'");
        return NULL;
    }
   
    if (request_msg.type() != JSON_OBJECT)
    {
        Print("Invalid type for key 'msg' (expected object)");
        return NULL;
    }
    
    JsonValue response;

    m_dispatcher.dispatch(cmd, *request_msg, response);

    return response.serialize();
}

/////////////////////////////////////////////////////////////////////////////
/// @brief Extracts the command and data from a message to a dispatcher.
///
/// The function `ParseRequestAndDispatch()` deserializes `request` into a
/// JSON object, which is expected to have the following schema:
/// {
///   'cmd': string,
///   'data': object
/// }
///
/// If either deserialization fails or any of the above JSON keys are not
/// found, returns `false`.
///
/// Otherwise, effectively invokes `dispatcher.Dispatch(cmd, data, reply)`,
/// where `cmd` and `data` are the values extracted from the JSON object,
/// and returns the result of the invocation.
///
/////////////////////////////////////////////////////////////////////////////

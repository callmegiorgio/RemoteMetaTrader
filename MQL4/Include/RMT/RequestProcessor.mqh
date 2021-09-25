#property strict

// Local
#include "Protocol/CloseOrderHandler.mqh"
#include "Protocol/GetBarsHandler.mqh"
#include "Protocol/GetTickHandler.mqh"
#include "Protocol/InvalidCommandHandler.mqh"
#include "Protocol/PlaceOrderHandler.mqh"
#include "Protocol/WatchSymbolHandler.mqh"
#include "MessageDispatcher.mqh"

class RequestProcessor {
public:
    RequestProcessor();
    
    /// TODO: use a logging class instead of `verbose`
    string process(const string& request, bool verbose = false);

private:
    MessageDispatcher m_dispatcher;
};

//===========================================================================
// --- RequestProcessor implementation ---
//===========================================================================
RequestProcessor::RequestProcessor()
{
    m_dispatcher.set_fallback_handler(new InvalidCommandHandler());
    m_dispatcher.set_handler("watch_symbol", new WatchSymbolHandler());
    m_dispatcher.set_handler("get_tick",     new GetTickHandler());
    m_dispatcher.set_handler("get_bars",     new GetBarsHandler());
    m_dispatcher.set_handler("place_order",  new PlaceOrderHandler());
    m_dispatcher.set_handler("close_order",  new CloseOrderHandler());
}

string RequestProcessor::process(const string& request, bool verbose)
{
    const JsonValue json_request = JsonValue::deserialize(request);

    if (!json_request)
    {
        if (verbose)
            Print("Failed to deserialize request");

        return NULL;
    }
    
    const JsonValue* json_cmd = json_request.find("cmd");

    if (!json_cmd)
    {
        if (verbose)
            Print("Request is missing key 'cmd'");

        return NULL;
    }

    bool ok;
    const string cmd = json_cmd.to_string(ok);

    if (!ok)
    {
        if (verbose)
            Print("Invalid type for key 'cmd' (expected string)");
            
        return NULL;
    }
    
    const JsonValue* request_msg = json_request.find("msg");
    
    if (!request_msg)
    {
        if (verbose)
            Print("Request is missing key 'msg'");
            
        return NULL;
    }
   
    if (request_msg.type() != JSON_OBJECT)
    {
        if (verbose)
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

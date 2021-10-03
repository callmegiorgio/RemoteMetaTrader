#property strict

// Local
#include "../Network/Server.mqh"
#include "CommandExecutor.mqh"

class RequestProcessor {
public:
    RequestProcessor(Server& the_server, TickEventPublisher& tick_publisher);
    
    /// Processes requests pending on the REQ socket until no request is
    /// pending or `timeout_ms` is reached. If `timeout_ms` is 0, then
    /// keeps processing requests indefinitely until none is received.
    void process_requests(uint timeout_ms = 50);

private:
    string process_one(string request);

    Server*         m_server;
    CommandExecutor m_cmd_executor;
};

//===========================================================================
// --- RequestProcessor implementation ---
//===========================================================================
RequestProcessor::RequestProcessor(Server& the_server, TickEventPublisher& tick_publisher)
    : m_server(GetPointer(the_server))
    , m_cmd_executor(tick_publisher)
{}

void RequestProcessor::process_requests(uint timeout_ms)
{
    const uint stop_tick_count = (timeout_ms != 0) ? (GetTickCount() + timeout_ms) : 0;

    while (true)
    {
        string request;

        if (!server.recv_request(request))
            break;

        Print("received request: ", request);

        const string response = process_one(request);

        Print("sending response: ", response);

        server.send_response(response);

        if (stop_tick_count != 0 && GetTickCount() >= stop_tick_count)
            break;
    }
}

string RequestProcessor::process_one(string request)
{
    const int len = StringLen(request);

    if (len == 0)
        return IntegerToString(CommandResult::INVALID_REQUEST);

    int i = 0;
    for (; i < len; i++)
    {
        const ushort c = request[i];

        if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z'))
            continue;
        else
            break;
    }

    CommandResult cmd_result;

    if (i == len)
    {
        // If control reaches here, that means we iterated over the entire
        // `request` string and didn't find any non-alphabetic character.
        // So, consider `request` to be a command with no content.

        const JsonValue json_request;
        cmd_result = m_cmd_executor.execute(request, json_request);
    }
    else
    {
        const int    next_index    = i + 1;
        const bool   is_last_index = (next_index == len);
        const ushort sep           = request[i];

        // If control enters this if-block, that means either we
        // found a non-alphabetic character at the very end of the
        // `request` string, or it's not at the very end, but the
        // character is not a space either. In any case, this is
        // an invalid request format.
        if (is_last_index || sep != ' ')
            return IntegerToString(CommandResult::INVALID_REQUEST);

        const string command         = StringSubstr(request, 0, i);
        const string request_content = StringSubstr(request, next_index);
        const JsonValue json_request = JsonValue::deserialize(request_content);

        cmd_result = m_cmd_executor.execute(command, json_request);
    }

    const string response_content = cmd_result.message().serialize();
    
    string response = IntegerToString(cmd_result.code());

    if (response_content != NULL && response_content != "")
    {
        response += " ";
        response += response_content;
    }

    return response;
}
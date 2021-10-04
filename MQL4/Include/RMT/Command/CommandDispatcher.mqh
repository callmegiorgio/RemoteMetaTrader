#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "../Utility/JsonWriter.mqh"
#include "Request/All.mqh"
#include "Response/All.mqh"
#include "CommandArguments.mqh"
#include "CommandResult.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Dispatches commands to be executed by a subclass.
///
/// The class `CommandDispatcher` maps command strings to `execute()` methods
/// such that commands received from network requests are easily handled by a
/// subclass after such requests have been validated.
///
/// Each JSON request has a corresponding MQL-native data type that allows a
/// straightforward, type-safe manipulation of the data contained in such
/// requests. Requests that return a content in their response also have a
/// corresponding MQL-native data type for the response data.
///
/// As such, business logic related to trading operations are abstracted away
/// from parsing of network data. In other words, the class `CommandDispather`
/// is JSON-aware, whereas its subclasses only need to think about the MQL
/// language.
///
/// Another advantage that this class provides is a faster lookup of commands,
/// compared to the alternative of using if-else branches, which takes a O(N)
/// performance. Since this class uses an internal hash map for string lookup,
/// a command lookup made on a call to `execute()` should take less than O(N).
///
////////////////////////////////////////////////////////////////////////////////
class CommandDispatcher {
public:
    CommandDispatcher();
    ~CommandDispatcher();

    ////////////////////////////////////////////////////////////////////////////////
    /// Executes a command received from a network request.
    ///
    /// Looks for a command-executing method identified by `command`. If no such a
    /// method is found, returns `CommandResult::UNKNOWN_REQUEST_COMMAND`.
    ///
    /// If a method is found, tries to deserialize `content` into a MQL-native
    /// object associated with `command`. If deserialization fails, returns a
    /// command result that stores the code and information about the failure.
    ///
    /// If deserialization succeeds, proceeds to invoke the command-executing method
    /// associated with `command` and retrieves the result of the invocation. If the
    /// method has an associated response object and the result of the invocation
    /// has code `CommandResult::SUCCESS`, the response parameter passed in to the
    /// command-executing method is serialized into the command result before it is
    /// returned. Otherwise, if the result code is not `CommandResult::SUCCESS`, the
    /// response parameter is ignored, and the result object is returned unchanged.
    ///
    /// @param command A request command.
    /// @param content A request content.
    /// @return Result of executing the command.
    ///
    ////////////////////////////////////////////////////////////////////////////////
    CommandResult execute(string command, const JsonValue& content);

protected:
    virtual CommandResult execute(const WatchSymbolRequest&    request) = 0;
    virtual CommandResult execute(const GetTickRequest&        request, GetTickResponse&        response) = 0;
    virtual CommandResult execute(const GetCurrentBarRequest&  request, GetCurrentBarResponse&  response) = 0;
    virtual CommandResult execute(const GetHistoryBarsRequest& request, GetHistoryBarsResponse& response) = 0;
    virtual CommandResult execute(const GetOrderRequest&       request, GetOrderResponse&       response) = 0;
    virtual CommandResult execute(const PlaceOrderRequest&     request, PlaceOrderResponse&     response) = 0;
    virtual CommandResult execute(const CloseOrderRequest&     request, CloseOrderResponse&     response) = 0;
    virtual CommandResult execute(const ModifyOrderRequest&    request) = 0;

private:
    typedef CommandResult(*ExecuteFunctionPointer)(CommandDispatcher&, CommandArguments&);

    class FunctionWrapper {
    public:
        ExecuteFunctionPointer execute;
    };

    template <typename RequestType>
    static CommandResult execute_responseless_command(CommandDispatcher& instance, CommandArguments& args);

    template <typename RequestType, typename ResponseType>
    static CommandResult execute_responseful_command(CommandDispatcher& instance, CommandArguments& args);

    template <typename RequestType>
    void register_responseless_command(string command);

    template <typename RequestType, typename ResponseType>
    void register_responseful_command(string command);

    void register_command(string command, ExecuteFunctionPointer execute_fn);

    HashMap<string, FunctionWrapper*> m_execute_wrappers;
};

//===========================================================================
// --- CommandDispatcher implementation ---
//===========================================================================
template <typename RequestType>
static CommandResult CommandDispatcher::execute_responseless_command(CommandDispatcher& instance, CommandArguments& args)
{
    RequestType request;

    if (!request.deserialize(args))
        return args.result();

    return instance.execute(request);
}

template <typename RequestType, typename ResponseType>
static CommandResult CommandDispatcher::execute_responseful_command(CommandDispatcher& instance, CommandArguments& args)
{
    RequestType request;

    if (!request.deserialize(args))
        return args.result();

    ResponseType response;
    CommandResult cmd_result = instance.execute(request, response);

    if (cmd_result.code() == CommandResult::SUCCESS)
    {
        JsonWriter writer(cmd_result.message());

        writer.write(response);
    }

    return cmd_result;
}

CommandDispatcher::CommandDispatcher()
{
    register_responseless_command<WatchSymbolRequest>("watchSymbol");
    register_responseless_command<ModifyOrderRequest>("modifyOrder");

    register_responseful_command<GetTickRequest,        GetTickResponse       >("getTick");
    register_responseful_command<GetCurrentBarRequest,  GetCurrentBarResponse >("getCurrentBar");
    register_responseful_command<GetHistoryBarsRequest, GetHistoryBarsResponse>("getHistoryBars");
    register_responseful_command<GetOrderRequest,       GetOrderResponse      >("getOrder");
    register_responseful_command<PlaceOrderRequest,     PlaceOrderResponse    >("placeOrder");
    register_responseful_command<CloseOrderRequest,     CloseOrderResponse    >("closeOrder");
}

CommandDispatcher::~CommandDispatcher()
{
    foreachm(string, command, FunctionWrapper*, wrapper, m_execute_wrappers)
        delete wrapper;
}

template <typename RequestType>
void CommandDispatcher::register_responseless_command(string command)
{
    register_command(command, execute_responseless_command<RequestType>);
}

template <typename RequestType, typename ResponseType>
void CommandDispatcher::register_responseful_command(string command)
{
    register_command(command, execute_responseful_command<RequestType, ResponseType>);
}

void CommandDispatcher::register_command(string command, ExecuteFunctionPointer execute_fn)
{
    if (execute_fn == NULL)
        return;

    FunctionWrapper* wrapper = m_execute_wrappers.get(command, NULL);

    if (wrapper != NULL)
    {
        wrapper.execute = execute_fn;
        return;
    }
    
    wrapper = new FunctionWrapper;
    wrapper.execute = execute_fn;

    m_execute_wrappers.set(command, wrapper);
}

CommandResult CommandDispatcher::execute(string command, const JsonValue& content)
{
    FunctionWrapper* wrapper = m_execute_wrappers.get(command, NULL);

    if (wrapper == NULL)
        return CommandResult::UNKNOWN_REQUEST_COMMAND;

    CommandArguments args(content);

    return wrapper.execute(this, args);
}
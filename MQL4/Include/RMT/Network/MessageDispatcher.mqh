#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "../Utility/JsonValue.mqh"
#include "MessageHandler.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Dispatches a request to a message handler.
///
/// The purpose of this class is to allow dynamic subscription of commands and
/// their respective processing. That is, instead of writing it like this:
/// @code
/// if (cmd == "command_a")
///     processCommandA(message_data);
/// else if (cmd == "command_b")
///     processCommandB(message_data);
/// else if (...)
/// @endcode
///
/// one can simply write:
///
/// @code
/// MessageDispatcher dispatcher;
/// dispatcher.set_handler("command_a", new MyCommandHandlerA());
/// dispatcher.set_handler("command_b", new MyCommandHandlerB());
/// @endcode
///
////////////////////////////////////////////////////////////////////////////////
class MessageDispatcher {
public:
    /// Constructs a message dispatcher.
    MessageDispatcher();
    
    /// Destroys a message dispatcher.
    ~MessageDispatcher();

    ////////////////////////////////////////////////////////////////////////////////
    /// @brief Sets the message handler for `command`.
    ///
    /// The method `SetHandler()` stores the `handler` object and associates it with
    /// `command` to be invoked by a call to `Dispatch()`.
    ///
    /// If a message handler is already stored, calling this method will destroy the
    /// the stored handler and replace it with `handler`.
    ///
    /// @param command A command to handle.
    /// @param handler A handler.
    ///
    ////////////////////////////////////////////////////////////////////////////////
    void set_handler(string command, MessageHandler* handler);
    
    void set_fallback_handler(MessageHandler* handler);

    /////////////////////////////////////////////////////////////////////////////
    /// @brief Dispatches a request to a registered message handler.
    ///
    ///
    /////////////////////////////////////////////////////////////////////////////
    void dispatch(string command, const JsonValue& message, JsonValue& response);

private:
    HashMap<string, MessageHandler*> m_message_handlers;
    MessageHandler* m_fallback_handler;
};

//===========================================================================
// --- MessageDispatcher implementation ---
//===========================================================================
MessageDispatcher::MessageDispatcher()
{
    m_fallback_handler = NULL;
}

MessageDispatcher::~MessageDispatcher()
{
    foreachm(string, key, MessageHandler*, handler, m_message_handlers)
        delete handler;

    if (m_fallback_handler != NULL)
        delete m_fallback_handler;
}

void MessageDispatcher::set_handler(string command, MessageHandler* handler)
{
    MessageHandler* old_handler = m_message_handlers[command];
    
    if (old_handler != NULL)
        delete old_handler;

    if (handler != NULL)
        m_message_handlers.set(command, handler);
}

void MessageDispatcher::set_fallback_handler(MessageHandler* handler)
{
    if (m_fallback_handler != NULL)
        delete m_fallback_handler;

    m_fallback_handler = handler;
}

void MessageDispatcher::dispatch(string command, const JsonValue& message, JsonValue& response)
{
    MessageHandler* handler = m_message_handlers[command];
    
    if (handler != NULL)
    {
        handler.process(message, response);
        return;
    }
    
    if (m_fallback_handler != NULL)
        m_fallback_handler.process(message, response);
}
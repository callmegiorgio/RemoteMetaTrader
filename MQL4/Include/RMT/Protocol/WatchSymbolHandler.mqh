#property strict

// Local
#include "../MessageHandler.mqh"
#include "../TickEventWatcher.mqh"

/// Request:
/// {
///   "symbol": string,
///   "should_watch": bool
/// }
///
/// Response:
/// {
///   "result": integer,
///   "symbols": ?array[string]
/// }
class WatchSymbolHandler : public MessageHandler {
public:
    WatchSymbolHandler(TickEventWatcher& tick_watcher)
    {
        m_tick_watcher = GetPointer(tick_watcher);
    }

private:
    void process() override
    {
        string symbol;
        bool should_watch;
        
        if (!read_required("symbol",       symbol))       return;
        if (!read_required("should_watch", should_watch)) return;
        
        if (should_watch)
        {
            if (symbol == "*")
                m_tick_watcher.fill();
            else
                m_tick_watcher.insert(symbol);
        }
        else
        {
            if (symbol == "*")
                m_tick_watcher.clear();
            else
                m_tick_watcher.remove(symbol);
        }

        write_result_success();
    }

    TickEventWatcher* m_tick_watcher;
};
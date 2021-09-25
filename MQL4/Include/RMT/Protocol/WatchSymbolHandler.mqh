#property strict

// Local
#include "../MessageHandler.mqh"
#include "../SymbolWatcher.mqh"

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
                SymbolWatcher::instance().fill();
            else
                SymbolWatcher::instance().insert(symbol);
        }
        else
        {
            if (symbol == "*")
                SymbolWatcher::instance().clear();
            else
                SymbolWatcher::instance().remove(symbol);
        }

        write_result_success();
    }
};
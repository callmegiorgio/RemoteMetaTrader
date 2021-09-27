#property strict

// Local
#include "../../MessageHandler.mqh"
#include "../../TickEventWatcher.mqh"

/// Request:
/// {
///   "symbol": string
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
        
        if (!read_required("symbol", symbol))
            return;
        
        if (symbol == "*")
        {
            const int n = SymbolsTotal(false);

            JsonValue symbols;
                
            for (int i = 0; i < n; i++)
            {
                const string s = SymbolName(i, false);

                m_tick_watcher.insert(s);
                symbols[i] = s;
            }

            write_value("symbols", symbols);
        }
        else
            m_tick_watcher.insert(symbol);

        write_result_success();
    }

    TickEventWatcher* m_tick_watcher;
};
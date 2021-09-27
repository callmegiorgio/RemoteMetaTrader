#property strict

// Local
#include "../../Network/MessageHandler.mqh"
#include "../../Network/TickEventPublisher.mqh"

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
    WatchSymbolHandler(TickEventPublisher& tick_publisher)
    {
        m_tick_publisher = GetPointer(tick_publisher);
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

                m_tick_publisher.insert(s);
                symbols[i] = s;
            }

            write_value("symbols", symbols);
        }
        else
            m_tick_publisher.insert(symbol);

        write_result_success();
    }

    TickEventPublisher* m_tick_publisher;
};
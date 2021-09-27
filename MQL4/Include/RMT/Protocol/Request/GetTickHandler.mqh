#property strict

// Local
#include "../../Network/MessageHandler.mqh"

/// Request:
/// {
///   "symbol": string
/// }
///
/// Response:
/// {
///   "server_time": datetime,
///   "bid": float,
///   "ask": float
/// }
class GetTickHandler : public MessageHandler {
private:
    void process() override
    {
        string symbol;

        if (!read_required("symbol", symbol))
            return;

        MqlTick last_tick;
        
        if (!SymbolInfoTick(symbol, last_tick))
        {
            write_result_last_error();
            return;
        }

        write_value("server_time", last_tick.time);
        write_value("bid",         last_tick.bid);
        write_value("ask",         last_tick.ask);
        write_result_success();
    }
};
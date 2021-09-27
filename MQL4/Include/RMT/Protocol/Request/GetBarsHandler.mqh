#property strict

// Local
#include "../../Network/MessageHandler.mqh"

/// Request:
/// {
///   "symbol": string,
///   "start_time": datetime,
///   "end_time": datetime
/// }
///
/// Response:
/// {
///   "result": integer,
///   "bars": [
///       [datetime, float, float, float, float],
///       [datetime, float, float, float, float],
///       ...
///   ]
/// }
class GetBarsHandler : public MessageHandler {
private:
    void process() override
    {
        string   symbol;
        datetime start_time = 0;
        datetime end_time;
        
        if (!read_required("symbol", symbol))
            return;

        read_optional("start_time", start_time);
        
        if (!read_optional("end_time", end_time))
        {
            // According to the MQL4 documentation, this is the last valid date
            // for `datetime`.
            MqlDateTime dt;
            dt.year = 3000;
            dt.mon  = 12;
            dt.day  = 31;
            dt.hour = 00;
            dt.min  = 00;
            dt.sec  = 00;

            end_time = StructToTime(dt);
        }

        MqlRates rates[];
        const int rates_count = CopyRates(symbol, PERIOD_M1, start_time, end_time, rates);

        if (rates_count == -1)
        {
            write_result_last_error();
            return;
        }

        JsonValue bars(JSON_ARRAY);

        for (int i = 0; i < rates_count; i++)
        {
            JsonValue* b = bars[i];

            b[0] = rates[i].time;
            b[1] = rates[i].open;
            b[2] = rates[i].high;
            b[3] = rates[i].low;
            b[4] = rates[i].close;
        }

        write_value("bars", bars);
        write_result_success();
    }
};
#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// Request:
/// {
///   "symbol":     string,
///   "start_time": datetime,
///   "end_time":   datetime
/// }
class GetBarsRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        if (!reader.read("symbol", this.symbol))
            return false;

        if (!reader.read("start_time", this.start_time, true))
            this.start_time = 0;
        
        if (!reader.read("end_time", this.end_time, true))
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

            this.end_time = StructToTime(dt);
        }
        
        return true;
    }

    string symbol;
    datetime start_time;
    datetime end_time;
};
#property strict

// Local
#include "../../Utility/JsonReader.mqh"
#include "../../Utility/Optional.mqh"

/// Request:
/// {
///   "symbol":     string,
///   "timeframe":  string,
///   "start_time": ?datetime,
///   "end_time":   ?datetime
/// }
class GetHistoryBarsRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        string timeframe_str;

        if (!reader.read_required("symbol",    this.symbol))   return false;
        if (!reader.read_required("timeframe", timeframe_str)) return false;

        if      (timeframe_str == "M1")  this.timeframe = PERIOD_M1;
        else if (timeframe_str == "M5")  this.timeframe = PERIOD_M5;
        else if (timeframe_str == "M15") this.timeframe = PERIOD_M15;
        else if (timeframe_str == "M30") this.timeframe = PERIOD_M30;
        else if (timeframe_str == "H1")  this.timeframe = PERIOD_H1;
        else if (timeframe_str == "H4")  this.timeframe = PERIOD_H4;
        else if (timeframe_str == "D1")  this.timeframe = PERIOD_D1;
        else if (timeframe_str == "W1")  this.timeframe = PERIOD_W1;
        else if (timeframe_str == "MN1") this.timeframe = PERIOD_MN1;
        else                             this.timeframe = ENUM_TIMEFRAMES(-1);

        reader.read_optional("start_time", this.start_time);
        reader.read_optional("end_time",   this.end_time);

        return true;
    }

    string             symbol;
    ENUM_TIMEFRAMES    timeframe;
    Optional<datetime> start_time;
    Optional<datetime> end_time;
};
#property strict

// Local
#include "../../Utility/JsonReader.mqh"
#include "../../Utility/Optional.mqh"

/// Request:
/// {
///   "symbol":     string,
///   "start_time": ?datetime,
///   "end_time":   ?datetime
/// }
class GetBarsRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        if (!reader.read_required("symbol", this.symbol))
            return false;

        reader.read_optional("start_time", this.start_time);
        reader.read_optional("end_time",   this.end_time);

        return true;
    }

    string             symbol;
    Optional<datetime> start_time;
    Optional<datetime> end_time;
};
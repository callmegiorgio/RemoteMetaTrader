#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// Request:
/// {
///   "symbol": string
/// }
class GetTickRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        return reader.read("symbol", this.symbol);
    }

    string symbol;
};
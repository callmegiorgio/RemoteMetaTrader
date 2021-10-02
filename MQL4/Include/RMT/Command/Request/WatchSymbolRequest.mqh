#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// {
///   "symbol": string
/// }
class WatchSymbolRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        return reader.read("symbol", this.symbol);
    }

    string symbol;
};
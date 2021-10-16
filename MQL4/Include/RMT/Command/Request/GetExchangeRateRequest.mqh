#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// Request:
/// {
///   "bcurrency": string,
///   "qcurrency": string
/// }
class GetExchangeRateRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        return (
            reader.read_required("bcurrency", this.base_currency) &&
            reader.read_required("qcurrency", this.quote_currency)
        );
    }

    string base_currency;
    string quote_currency;
};
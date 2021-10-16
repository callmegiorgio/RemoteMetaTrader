#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// {
///   "rate": double
/// }
class GetExchangeRateResponse {
public:
    void write(JsonWriter& writer) const
    {
        writer.write("rate", this.rate);
    }

    double rate;
};
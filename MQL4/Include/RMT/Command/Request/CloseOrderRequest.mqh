#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// Request:
/// {
///   "ticket":   integer,
///   "lots":     ?double,
///   "price":    ?double,
///   "slippage": ?integer
/// }
class CloseOrderRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        if (!reader.read_required("ticket", this.ticket))
            return false;

        reader.read_optional("lots",     this.lots);
        reader.read_optional("price",    this.price);
        reader.read_optional("slippage", this.slippage);

        return true;
    }

    int              ticket;
    Optional<double> lots;
    Optional<double> price;
    Optional<int>    slippage;
};
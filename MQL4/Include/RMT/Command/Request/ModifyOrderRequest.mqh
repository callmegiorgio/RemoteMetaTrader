#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// Request:
/// {
///   "ticket":     integer,
///   "sl":         ?double,
///   "tp":         ?double,
///   "price":      ?double,
///   "expiration": ?integer
/// }
class ModifyOrderRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        if (!reader.read_required("ticket", this.ticket))
            return false;

        reader.read_optional("sl",         this.stop_loss);
        reader.read_optional("tp",         this.take_profit);
        reader.read_optional("price",      this.price);
        reader.read_optional("expiration", this.expiration);

        return true;
    }

    int                ticket;
    Optional<double>   stop_loss;
    Optional<double>   take_profit;
    Optional<double>   price;
    Optional<datetime> expiration;
};
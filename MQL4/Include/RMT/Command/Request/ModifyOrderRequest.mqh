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
        if (!reader.read("ticket", this.ticket))
            return false;

        if (!reader.read("sl",         this.stop_loss,   true)) this.stop_loss   = -1;
        if (!reader.read("tp",         this.take_profit, true)) this.take_profit = -1;
        if (!reader.read("price",      this.price,       true)) this.price       = -1;
        if (!reader.read("expiration", this.expiration,  true)) this.expiration  = 0;

        return true;
    }

    int      ticket;
    double   stop_loss;
    double   take_profit;
    double   price;
    datetime expiration;
};
#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// Request:
/// {
///   "ticket":   integer,
///   "lots":     ?double  = -1.0,
///   "price":    ?double  = -1.0,
///   "slippage": ?integer = 0
/// }
class CloseOrderRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        if (!reader.read("ticket", this.ticket))
            return false;

        if (!reader.read("lots",     this.lots,     true)) this.lots  = -1.0;
        if (!reader.read("price",    this.price,    true)) this.price = -1.0;
        if (!reader.read("slippage", this.slippage, true)) this.slippage = 0;

        return true;
    }

    int    ticket;
    double lots;
    double price;
    int    slippage;
};
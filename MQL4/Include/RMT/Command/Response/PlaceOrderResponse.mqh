#property strict

// Local
#include "../../Utility/JsonValue.mqh"

/// Response:
/// {
///   "ticket":     integer,
///   "lots":       ?double,
///   "op":         ?double,
///   "ot":         ?datetime,
///   "commission": ?double,
///   "profit":     ?double,
///   "swap":       ?double
/// }
class PlaceOrderResponse {
public:
    void serialize(JsonValue& content)
    {
        content["ticket"]     = this.ticket;
        content["lots"]       = this.lots;
        content["op"]         = this.open_price;
        content["ot"]         = this.open_time;
        content["commission"] = this.commission;
        content["profit"]     = this.profit;
        content["swap"]       = this.swap;
    }

    int      ticket;
    double   lots;
    double   open_price;
    datetime open_time;
    double   commission;
    double   profit;
    double   swap;
};
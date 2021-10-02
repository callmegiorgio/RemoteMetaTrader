#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

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
    void write(JsonWriter& writer) const
    {
        writer.write("ticket",     this.ticket);
        writer.write("lots",       this.lots);
        writer.write("op",         this.open_price);
        writer.write("ot",         this.open_time);
        writer.write("commission", this.commission);
        writer.write("profit",     this.profit);
        writer.write("swap",       this.swap);
    }

    int                ticket;
    Optional<double>   lots;
    Optional<double>   open_price;
    Optional<datetime> open_time;
    Optional<double>   commission;
    Optional<double>   profit;
    Optional<double>   swap;
};
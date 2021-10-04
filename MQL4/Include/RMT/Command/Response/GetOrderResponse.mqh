#property strict

// Local
#include "../../Utility/JsonWriter.mqh"
#include "../../Utility/Optional.mqh"

/// Response:
/// {
///   "opcode":     integer,
///   "status":     string,
///   "symbol":     string,
///   "lots":       double,
///   "op":         double,
///   "ot":         datetime,
///   "cp":         ?double,
///   "ct":         ?datetime,
///   "sl":         ?double,
///   "tp":         ?double,
///   "expiration": ?datetime,
///   "comment":    string,
///   "magic":      integer,
///   "commission": double,
///   "profit":     double,
///   "swap":       double
/// }
class GetOrderResponse {
public:
    void write(JsonWriter& writer) const
    {
        writer.write("opcode",     this.opcode);
        writer.write("status",     this.status);
        writer.write("symbol",     this.symbol);
        writer.write("lots",       this.lots);
        writer.write("op",         this.open_price);
        writer.write("ot",         this.open_time);
        writer.write("cp",         this.close_price);
        writer.write("ct",         this.close_time);
        writer.write("sl",         this.stop_loss);
        writer.write("tp",         this.take_profit);
        writer.write("expiration", this.expiration);
        writer.write("comment",    this.comment);
        writer.write("magic",      this.magic_number);
        writer.write("commission", this.commission);
        writer.write("profit",     this.profit);
        writer.write("swap",       this.swap);
    }

    int                opcode;
    string             status;
    string             symbol;
    double             lots;
    double             open_price;
    datetime           open_time;
    Optional<double>   close_price;
    Optional<datetime> close_time;
    Optional<double>   stop_loss;
    Optional<double>   take_profit;
    Optional<datetime> expiration;
    string             comment;
    int                magic_number;
    double             commission;
    double             profit;
    double             swap;
};
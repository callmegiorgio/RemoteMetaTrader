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
///   "ot":         string,
///   "cp":         ?double,
///   "ct":         ?string,
///   "sl":         ?double,
///   "tp":         ?double,
///   "expiration": ?string,
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
        writer.write("ot",         TimeToStr(this.open_time, TIME_DATE|TIME_SECONDS));
        writer.write("cp",         this.close_price);

        if (this.close_time.has_value())
            writer.write("ct", TimeToStr(this.close_time.value()));

        writer.write("sl",         this.stop_loss);
        writer.write("tp",         this.take_profit);

        if (this.expiration.has_value())
            writer.write("expiration", TimeToStr(this.expiration.value()));

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
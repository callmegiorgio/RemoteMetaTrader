#property strict

// Local
#include "../../Utility/JsonReader.mqh"
#include "../../Utility/Optional.mqh"

/// Request:
/// {
///   "symbol":     string,
///   "opcode":     integer,
///   "lots":       double,
///   "price":      ?double,
///   "slippage":   ?integer,
///   "sl":         ?double,
///   "tp":         ?double,
///   "comment":    ?string,
///   "magic":      ?integer,
///   "expiration": ?datetime
/// }
class PlaceOrderRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        if (!reader.read_required("symbol", symbol)) return false;
        if (!reader.read_required("opcode", opcode)) return false;
        if (!reader.read_required("lots",   lots))   return false;

        reader.read_optional("price",      this.price);
        reader.read_optional("slippage",   this.slippage);
        reader.read_optional("sl",         this.stop_loss);
        reader.read_optional("tp",         this.take_profit);
        reader.read_optional("comment",    this.comment);
        reader.read_optional("magic",      this.magic_number);
        reader.read_optional("expiration", this.expiration);

        return true;
    }

    string             symbol;
    int                opcode;
    double             lots;
    Optional<double>   price;
    Optional<int>      slippage;
    Optional<double>   stop_loss;
    Optional<double>   take_profit;
    Optional<string>   comment;
    Optional<int>      magic_number;
    Optional<datetime> expiration;
};
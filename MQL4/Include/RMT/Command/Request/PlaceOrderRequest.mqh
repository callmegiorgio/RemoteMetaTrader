#property strict

// Local
#include "../../Utility/JsonReader.mqh"

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
        if (!reader.read("symbol", symbol)) return false;
        if (!reader.read("opcode", opcode)) return false;
        if (!reader.read("lots",   lots))   return false;

        if (!reader.read("price",      this.price,        true)) this.price        = -1;
        if (!reader.read("slippage",   this.slippage,     true)) this.slippage     = 0;
        if (!reader.read("sl",         this.stop_loss,    true)) this.stop_loss    = 0;
        if (!reader.read("tp",         this.take_profit,  true)) this.take_profit  = 0;
        if (!reader.read("comment",    this.comment,      true)) this.comment      = "";
        if (!reader.read("magic",      this.magic_number, true)) this.magic_number = 0;
        if (!reader.read("expiration", this.expiration,   true)) this.expiration   = 0;

        return true;
    }

    string symbol;
    int    opcode;
    double lots;
    double price;
    int    slippage;
    double stop_loss;
    double take_profit;
    string comment;
    int    magic_number;
    int    expiration;
};
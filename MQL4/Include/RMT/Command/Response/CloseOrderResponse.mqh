#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

class CloseOrderResponseNewOrder {
public:
    CloseOrderResponseNewOrder()
    {}

    CloseOrderResponseNewOrder(const CloseOrderResponseNewOrder& other)
    {
        this.ticket       = other.ticket;
        this.lots         = other.lots;
        this.magic_number = other.magic_number;
        this.comment      = other.comment;
        this.commission   = other.commission;
        this.profit       = other.profit;
        this.swap         = other.swap;
    }

    void write(JsonWriter& writer) const
    {
        writer.write("ticket",     this.ticket);
        writer.write("lots",       this.lots);
        writer.write("magic",      this.magic_number);
        writer.write("comment",    this.comment);
        writer.write("commission", this.commission);
        writer.write("profit",     this.profit);
        writer.write("swap",       this.swap);
    }

    int    ticket;
    double lots;
    int    magic_number;
    string comment;
    double commission;
    double profit;
    double swap;
};

/// Response:
/// {
///   "cp":         double,
///   "ct":         string,
///   "lots":       double,
///   "comment":    ?string,
///   "commission": double,
///   "profit":     double,
///   "swap":       double,
///   "new_order":
///   ?{
///     "ticket":     integer,
///     "lots":       ?double,
///     "magic":      ?integer,
///     "comment":    ?string,
///     "commission": ?double,
///     "profit":     ?double,
///     "swap":       ?double
///   }
/// }
class CloseOrderResponse {
public:
    void write(JsonWriter& writer) const
    {
        writer.write("cp",         this.close_price);
        writer.write("ct",         TimeToStr(this.close_time));
        writer.write("lots",       this.lots);
        writer.write("comment",    this.comment);
        writer.write("commission", this.commission);
        writer.write("profit",     this.profit);
        writer.write("swap",       this.swap);
        writer.write("new_order",  this.new_order);
    }

    double   close_price;
    datetime close_time;
    double   lots;
    string   comment;
    double   commission;
    double   profit;
    double   swap;
    OptionalComplex<CloseOrderResponseNewOrder> new_order;
};
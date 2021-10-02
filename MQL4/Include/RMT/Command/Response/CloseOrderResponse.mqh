#property strict

// Local
#include "../../Utility/JsonValue.mqh"

/// Response:
/// {
///   "cp":         double,
///   "ct":         datetime,
///   "lots":       double,
///   "comment":    string,
///   "commission": double,
///   "profit":     double,
///   "swap":       double,
///   "new_order": ?{
///     "ticket":     integer,
///     "lots":       double,
///     "magic":      integer,
///     "comment":    string,
///     "commission": double,
///     "profit":     double,
///     "swap":       double
///   }
/// }
class CloseOrderResponse {
public:
    static const int NO_NEW_ORDER;

    void serialize(JsonValue& content)
    {
        content["cp"]         = this.close_price;
        content["ct"]         = this.close_time;
        content["lots"]       = this.lots;
        content["comment"]    = this.comment;
        content["commission"] = this.commission;
        content["profit"]     = this.profit;
        content["swap"]       = this.swap;

        if (new_order_ticket == CloseOrderResponse::NO_NEW_ORDER)
            return;
        
        JsonValue* new_order = content["new_order"];

        new_order["ticket"]     = this.new_order_ticket;
        new_order["lots"]       = this.new_order_lots;
        new_order["magic"]      = this.new_order_magic_number;
        new_order["comment"]    = this.new_order_comment;
        new_order["commission"] = this.new_order_commission;
        new_order["profit"]     = this.new_order_profit;
        new_order["swap"]       = this.new_order_swap;
    }

    double   close_price;
    datetime close_time;
    double   lots;
    string   comment;
    double   commission;
    double   profit;
    double   swap;
    int      new_order_ticket;
    double   new_order_lots;
    int      new_order_magic_number;
    string   new_order_comment;
    double   new_order_commission;
    double   new_order_profit;
    double   new_order_swap;
};

static const int CloseOrderResponse::NO_NEW_ORDER = -1;
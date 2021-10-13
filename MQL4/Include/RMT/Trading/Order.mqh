#property strict

/// Stores properties of an order.
class Order {
public:
    /// Updates the order's properties to values of the order currently selected
    /// by `OrderSelect()`.
    void refresh();

    string   symbol;
    double   lots;
    int      type;
    double   open_price;
    datetime open_time;
    double   close_price;
    datetime close_time;
    double   stop_loss;
    double   take_profit;
    datetime expiration;
    int      magic_number;
    string   comment;
    double   commission;
    double   profit;
    double   swap;
};

//===========================================================================
// --- Order implementation ---
//===========================================================================
void Order::refresh()
{
    this.symbol       = OrderSymbol();
    this.lots         = OrderLots();
    this.type         = OrderType();
    this.open_price   = OrderOpenPrice();
    this.open_time    = OrderOpenTime();
    this.close_price  = OrderClosePrice();
    this.close_time   = OrderCloseTime();
    this.stop_loss    = OrderStopLoss();
    this.take_profit  = OrderTakeProfit();
    this.expiration   = OrderExpiration();
    this.magic_number = OrderMagicNumber();
    this.comment      = OrderComment();
    this.commission   = OrderCommission();
    this.profit       = OrderProfit();
    this.swap         = OrderSwap();
}
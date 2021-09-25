#property strict

// Local
#include "../../MessageHandler.mqh"

/// Request:
/// {
///   "symbol": string,
///   "opcode": integer,
///   "lots": double,
///   "price": double,
///   "slippage": integer|undefined,
///   "sl": double|undefined,
///   "tp": double|undefined,
///   "comment": string|undefined,
///   "magic": integer|undefined,
///   "expiration": integer|undefined
/// }
///
/// Response:
/// {
///   "result": integer,
///   "ticket": integer|undefined,
///   "op": float|undefined,
///   "ot": datetime|undefined,
///   "lots": float|undefined,
///   "commission": float|undefined,
///   "profit": float|undefined
///   "swap": float|undefined
/// }
class PlaceOrderHandler : public MessageHandler {
private:
    void process() override
    {
        string   symbol;
        int      opcode;
        double   lots;
        double   price;
        int      slippage   = 0;
        double   stoploss   = 0;
        double   takeprofit = 0;
        string   comment    = "";
        int      magic      = 0;
        datetime expiration = 0;

        // Required values.
        if (!read_required("symbol", symbol)) return;
        if (!read_required("opcode", opcode)) return;
        if (!read_required("lots",   lots))   return;
        if (!read_required("price",  price))  return;

        // Optional values.
        read_optional("slippage",   slippage);
        read_optional("sl",         stoploss);
        read_optional("tp",         takeprofit);
        read_optional("comment",    comment);
        read_optional("magic",      magic);
        read_optional("expiration", expiration);
 
        // Order creation.
        const int ticket =
            OrderSend(
                symbol,
                opcode,
                lots,
                price,
                slippage,
                stoploss,
                takeprofit,
                comment,
                magic,
                expiration
           );

        if (ticket == -1)
        {
            write_result_last_error();
            return;
        }

        write_value("ticket", ticket);

        if (OrderSelect(ticket, SELECT_BY_TICKET))
        {
            const bool is_market_order = (opcode == OP_BUY || opcode == OP_SELL);

            if (is_market_order)
                write_value("op", OrderOpenPrice());
            else
                write_value("lots", OrderLots());

            write_value("ot",         OrderOpenTime());
            write_value("commission", OrderCommission());
            write_value("profit",     OrderProfit());
            write_value("swap",       OrderSwap());
        }

        write_result_success();
    }
};
#property strict

// Local
#include "../../Network/MessageHandler.mqh"
#include "../../Trading/Tick.mqh"

/// Request:
/// {
///   "symbol": string,
///   "opcode": integer,
///   "lots": double,
///   "price": double|undefined,
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
        
        if (!read_required("symbol", symbol)) return;
        if (!read_required("opcode", opcode)) return;
        if (!read_required("lots",   lots))   return;

        const int ticket = place_order(symbol, opcode, lots);

        if (ticket == -1)
            return;

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

    bool get_market_price(string symbol, int opcode, double& price)
    {
        Tick last_tick;

        if (!Tick::current(symbol, last_tick))
        {
            write_result_last_error();
            return false;
        }

        switch (opcode)
        {
            case OP_BUY:  price = last_tick.ask(); break;
            case OP_SELL: price = last_tick.bid(); break;

            default:
                write_result(-50); // TODO
                return false;
        }

        return true;
    }

    int place_order(string symbol, int opcode, double lots, uint retries = 3)
    {
        int      slippage   = 0;
        double   stoploss   = 0;
        double   takeprofit = 0;
        string   comment    = "";
        int      magic      = 0;
        datetime expiration = 0;

        read_optional("slippage",   slippage);
        read_optional("sl",         stoploss);
        read_optional("tp",         takeprofit);
        read_optional("comment",    comment);
        read_optional("magic",      magic);
        read_optional("expiration", expiration);

        double price;
        bool   should_get_market_price = (read_optional("price", price) == false);

        for (uint i = 1; true; i++)
        {
            if (should_get_market_price && !get_market_price(symbol, opcode, price))
                return -1;

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
            
            if (ticket != -1)
                return ticket;

            const int last_error = GetLastError();

            switch (last_error)
            {
                case ERR_REQUOTE:
                case ERR_PRICE_CHANGED:
                case ERR_OFF_QUOTES:
                    if (i < retries)
                        continue;
                    
                    // fallthrough

                default:
                    write_result(last_error);
                    return -1;
            }
        }
    }
};
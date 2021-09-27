#property strict

// 3rdparty
#include <Mql/Collection/HashSet.mqh>

// Local
#include "../../Network/MessageHandler.mqh"
#include "../../Trading/Tick.mqh"

/// Request:
/// {
///   "ticket": integer,
///   "price": float|undefined,
///   "slippage": integer|undefined
/// }
///
/// Response:
/// {
///   "result": integer
///   "cp": ?float
///   "ct": ?datetime
///   "lots": ?float
///   "comment": ?string
///   "commission": ?float
///   "profit": ?float
///   "swap": ?float
/// }
class CloseOrderHandler : public MessageHandler {
protected:
    bool read_and_select_ticket(int& ticket)
    {
        if (!read_required("ticket", ticket))
            return false;
        
        if (!OrderSelect(ticket, SELECT_BY_TICKET))
        {
            write_result_last_error();
            return false;
        }

        return true;
    }

    bool read_price(double& price)
    {
        if (read_optional("price", price))
            return true;

        Tick last_tick;

        if (!Tick::current(OrderSymbol(), last_tick))
        {
            write_result_last_error();
            return false;
        }

        switch (OrderType())
        {
            case OP_BUY:  price = last_tick.bid(); break;
            case OP_SELL: price = last_tick.ask(); break;

            default:
                write_result(-50); // TODO
                return false;
        }

        return true;
    }

    void read_slippage(int& slippage)
    {
        if (!read_optional("slippage", slippage))
            slippage = 3;
    }

    bool close_order(int ticket, double lots, uint retries = 2)
    {
        double price;
        int slippage;
        
        read_slippage(slippage);

        retries++;
        for (uint i = 0; i < retries; i++)
        {
            if (!read_price(price))
                return false;

            if (OrderClose(ticket, lots, price, slippage))
            {
                if (OrderSelect(ticket, SELECT_BY_TICKET))
                {
                    write_value("cp",         OrderClosePrice());
                    write_value("ct",         OrderCloseTime());
                    write_value("lots",       OrderLots());
                    write_value("comment",    OrderComment());
                    write_value("commission", OrderCommission());
                    write_value("profit",     OrderProfit());
                    write_value("swap",       OrderSwap());
                }

                return true;
            }
            
            switch (GetLastError())
            {
                case ERR_REQUOTE:
                case ERR_PRICE_CHANGED:
                case ERR_OFF_QUOTES:
                    continue;

                default:
                    write_result_last_error();
                    return false;
            }
        }

        write_result_last_error();
        return false;
    }

private:
    void process() override
    {
        int ticket;

        if (!read_and_select_ticket(ticket))
            return;
        
        if (!close_order(ticket, OrderLots()))
            return;

        write_result_success();
    }
};
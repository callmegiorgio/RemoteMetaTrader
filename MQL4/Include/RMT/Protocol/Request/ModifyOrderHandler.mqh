#property strict

// Local
#include "../../Network/MessageHandler.mqh"

/// Request:
/// {
///   "ticket": integer,
///   "sl": double,
///   "tp": double,
///   "price": double|undefined,
///   "expiration": integer|undefined
/// }
///
/// Response:
/// {
///   "result": integer
/// }
class ModifyOrderHandler : public MessageHandler {
private:
    void process() override
    {
        int      ticket;
        double   stop_loss;
        double   take_profit;
        double   price      = 0;
        datetime expiration = 0;
        
        if (!read_required("ticket", ticket))      return;
        if (!read_required("sl",     stop_loss))   return;
        if (!read_required("tp",     take_profit)) return;

        if (!OrderSelect(ticket, SELECT_BY_TICKET))
        {
            write_result_last_error();
            return;
        }

        switch (OrderType())
        {
            case OP_BUY:
            case OP_SELL:
                break;
            
            default:
                if (!read_optional("price", price))
                    price = OrderOpenPrice();
                
                if (!read_optional("expiration", expiration))
                    expiration = OrderExpiration();
        }

        if (!OrderModify(ticket, price, stop_loss, take_profit, expiration))
        {
            const int last_error = GetLastError();

            if (last_error != ERR_NO_RESULT)
            {
                write_result(last_error);
                return;
            }

            // Fallthrough. ERR_NO_RESULT means nothing changed because the given values
            // are identical to the current ones.
        }

        write_result_success();
    }
};
#property strict

// 3rdparty
#include <Mql/Collection/HashSet.mqh>

// Local
#include "../../Network/MessageHandler.mqh"

/// Request:
/// {
///   "ticket": integer,
///   "price": float,
///   "slippage": integer|undefined,
///   "lots": double|undefined
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
///   "remaining_order":
///   ?{
///     "ticket": integer
///     "lots": float
///     "comment": string
///     "commission": float
///     "profit": float
///     "swap": float
///   }
/// }
class CloseOrderHandler : public MessageHandler {
private:
    void process() override
    {
        int    ticket;
        double price;
        int    slippage = 0;
        double lots     = 0;

        // Required values.
        if (!read_required("ticket",   ticket)) return;
        if (!read_required("price",    price))  return;
        
        read_optional("slippage", slippage);
        read_optional("lots",     lots);

        if (!OrderSelect(ticket, SELECT_BY_TICKET))
        {
            write_result_last_error();
            return;
        }

        // Check if it's a total or partial close.
        const bool is_partial_close = lots < OrderLots();

        //==============================================================================
        // This seems the most reliable way of getting the ticket of the remaining order
        // after a partial close.
        //
        // The idea is to store the tickets of all open orders before closing an order.
        // Once an order is closed, remove its ticket from the set and iterate through
        // all open orders again. The ticket which was not previously stored must be the
        // remaining order's ticket.
        //
        // Example:
        // (Step 1) `ticket` == 10.
        // (Step 2) `tickets` before close of `ticket`: (1, 6, 10, 15).
        // (Step 3) `tickets` after close of `ticket` and its removal: (1, 6, 15).
        // (Step 4) The ticket which is not within `tickets` is the remaining order's.
        //==============================================================================
        HashSet<int> tickets;

        if (is_partial_close)
        {
            const int orders_count = OrdersTotal();

            for (int i = 0; i < orders_count; i++)
            {
                if (!OrderSelect(i, SELECT_BY_POS))
                {
                    write_result_last_error();
                    return;
                }

                tickets.add(OrderTicket());
            }
        }

        // Order closeup.
        if (!OrderClose(ticket, lots, price, slippage))
        {
            write_result_last_error();
            return;
        }

        // Retrieve information to client about the closed order, irrespective of
        // whether it's a partial or whole close.
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

        if (is_partial_close)
        {
            // Remove closed order's ticket from the set.
            tickets.remove(ticket);

            const int orders_count = OrdersTotal();

            // Iterate through all open orders to find the remaining order's ticket.
            for (int i = 0; i < orders_count; i++)
            {
                if (!OrderSelect(i, SELECT_BY_POS))
                    continue;
                
                if (!tickets.contains(OrderTicket()))
                {
                    JsonValue remaining_order;
                    remaining_order["ticket"]     = OrderTicket();
                    remaining_order["lots"]       = OrderLots();
                    remaining_order["comment"]    = OrderComment();
                    remaining_order["commission"] = OrderCommission();
                    remaining_order["profit"]     = OrderProfit();
                    remaining_order["swap"]       = OrderSwap();

                    write_value("remaining_order", remaining_order);
                    write_result_success();
                    return;
                }
            }

            // If control reaches here, that means a partial order was closed, but
            // we were unable to get the remaining order's ticket, likely due to a
            // failure of `OrderSelect()`. In that case, just fallthrough and return
            // a success result, since the partial order was effectively closed.
        }

        write_result_success();
    }
};
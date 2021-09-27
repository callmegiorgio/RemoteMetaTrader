#property strict

// 3rdparty
#include <Mql/Collection/HashSet.mqh>

// Local
#include "CloseOrderHandler.mqh"

/// Request:
/// {
///   "ticket": integer,
///   "lots": double,
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
///   "remaining_order":
///   {
///     "ticket": integer
///     "lots": float
///     "magic": integer
///     "comment": string
///     "commission": float
///     "profit": float
///     "swap": float
///   }
/// }
class PartialCloseOrderHandler : public CloseOrderHandler {
private:
    void process() override
    {
        int    ticket;
        double lots;

        if (!read_and_select_ticket(ticket))
            return;

        if (!read_required("lots", lots))
            return;

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

        if (!populate_tickets(tickets))
            return;
        
        if (!close_order(ticket, lots))
            return;

        // Remove closed order's ticket from the set.
        tickets.remove(ticket);

        if (select_remaining_order(tickets))
        {
            JsonValue remaining_order;
            remaining_order["ticket"]     = OrderTicket();
            remaining_order["lots"]       = OrderLots();
            remaining_order["magic"]      = OrderMagicNumber();
            remaining_order["comment"]    = OrderComment();
            remaining_order["commission"] = OrderCommission();
            remaining_order["profit"]     = OrderProfit();
            remaining_order["swap"]       = OrderSwap();

            write_value("remaining_order", remaining_order);
        }
        else
        {
            // If control reaches here, that means a partial order was closed, but
            // we were unable to get the remaining order's ticket, likely due to a
            // failure of `OrderSelect()`. In that case, just fallthrough and return
            // a success result, since the partial order was effectively closed.
        }

        write_result_success();
    }

    bool populate_tickets(HashSet<int>& tickets)
    {
        const int orders_count = OrdersTotal();

        for (int i = 0; i < orders_count; i++)
        {
            if (!OrderSelect(i, SELECT_BY_POS))
            {
                write_result_last_error();
                return false;
            }

            tickets.add(OrderTicket());
        }

        return true;
    }

    bool select_remaining_order(const HashSet<int>& tickets)
    {
        const int orders_count = OrdersTotal();

            // Iterate through all open orders to find the remaining order's ticket.
        for (int i = 0; i < orders_count; i++)
        {
            if (!OrderSelect(i, SELECT_BY_POS))
                continue;
            
            if (!tickets.contains(OrderTicket()))
                return true;
        }

        return false;
    }
};
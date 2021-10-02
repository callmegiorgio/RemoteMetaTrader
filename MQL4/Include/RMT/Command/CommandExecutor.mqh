#property strict

// 3rdparty
#include <Mql/Collection/HashSet.mqh>

// Local
#include "../Event/TickEventPublisher.mqh"
#include "../Trading/Tick.mqh"
#include "CommandDispatcher.mqh"

/// Implements the business logic interfaced by `CommandDispatcher`.
class CommandExecutor : public CommandDispatcher {
public:
    CommandExecutor(TickEventPublisher& tick_publisher);

private:
    CommandResult execute(const WatchSymbolRequest& request) override;
    CommandResult execute(const GetTickRequest& request, GetTickResponse& response) override;
    CommandResult execute(const GetBarsRequest& request, GetBarsResponse& response) override;
    CommandResult execute(const PlaceOrderRequest& request, PlaceOrderResponse& response) override;
    CommandResult execute(const CloseOrderRequest& request, CloseOrderResponse& response) override;
    CommandResult execute(const ModifyOrderRequest& request) override;

    TickEventPublisher* m_tick_publisher;
};

//===========================================================================
// --- CommandExecutor implementation ---
//===========================================================================
CommandExecutor::CommandExecutor(TickEventPublisher& tick_publisher)
{
    m_tick_publisher = GetPointer(tick_publisher);
}

CommandResult CommandExecutor::execute(const WatchSymbolRequest& request) override
{
    m_tick_publisher.insert(request.symbol);

    return CommandResult::SUCCESS;
}

CommandResult CommandExecutor::execute(const GetTickRequest& request, GetTickResponse& response) override
{
    if (!Tick::current(request.symbol, response.last_tick))
        return GetLastError();
    
    return CommandResult::SUCCESS;
}

CommandResult CommandExecutor::execute(const GetBarsRequest& request, GetBarsResponse& response) override
{
    response.rates_count =
        CopyRates(
            request.symbol,
            PERIOD_M1,
            request.start_time,
            request.end_time,
            response.rates
        );

    if (response.rates_count == -1)
        return GetLastError();

    return CommandResult::SUCCESS;
}

CommandResult CommandExecutor::execute(const PlaceOrderRequest& request, PlaceOrderResponse& response) override
{
    // Number of attempts to place an order in case a price requote happens.
    const uint tries = 3;

    // Indicates whether we should retrieve the last market price or use the price
    // given to us by the Client. If `request.price` is less than 0, that means the
    // Client didn't give us a price, so we'll be getting current quotes instead.
    const bool should_get_market_price = request.price < 0;

    double price = request.price;

    for (uint i = 1; i <= tries; i++)
    {
        if (should_get_market_price)
        {
            Tick last_tick;

            // If we failed to get price, try again in the next retries.
            if (!Tick::current(request.symbol, last_tick))
                continue;

            // We can only use the current market price to fill a market order.
            // If the Client asked us to place a pending order, the Client had
            // to provide the price, because it doesn't make sense to place
            // pending orders on current price.
            switch (request.opcode)
            {
                case OP_BUY:  price = last_tick.ask(); break;
                case OP_SELL: price = last_tick.bid(); break;

                default:
                    return CommandResult::INVALID_ORDER_STATUS;
            }
        }

        // Request trade server to place the order.
        const int ticket =
            OrderSend(
                request.symbol,
                request.opcode,
                request.lots,
                price,
                request.slippage,
                request.stop_loss,
                request.take_profit,
                request.comment,
                request.magic_number,
                request.expiration
            );
        
        if (ticket != -1)
        {
            response.ticket = ticket;
        
            if (OrderSelect(ticket, SELECT_BY_TICKET))
            {
                response.lots       = OrderLots();
                response.open_price = OrderOpenPrice();
                response.open_time  = OrderOpenTime();
                response.commission = OrderCommission();
                response.profit     = OrderProfit();
                response.swap       = OrderSwap();
            }

            return CommandResult::SUCCESS;
        }

        const int last_error = GetLastError();

        switch (last_error)
        {
            case ERR_REQUOTE:
            case ERR_PRICE_CHANGED:
            case ERR_OFF_QUOTES:
                continue;

            default:
                return last_error;
        }
    }

    return GetLastError();
}

CommandResult CommandExecutor::execute(const CloseOrderRequest& request, CloseOrderResponse& response) override
{
    if (!OrderSelect(request.ticket, SELECT_BY_TICKET))
        return GetLastError();

    const int optype = OrderType();

    // Ensure the selected order refers to a market order. Only market orders may be closed;
    // pending orders may be canceled, but not closed.
    switch (optype)
    {
        case OP_BUY:
        case OP_SELL:
            break;

        default:
            return CommandResult::make_invalid_order_status("pending", "filled");
    }

    const double is_lots_provided = (request.lots > 0);

    const double lots = is_lots_provided ? request.lots : OrderLots();
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
                return GetLastError();

            tickets.add(OrderTicket());
        }
    }

    // Number of attempts to close the order in case a price requote happens.
    const uint tries = 3;

    // Indicates whether we should retrieve the last market price or use the price
    // given to us by the Client. If `request.price` is less than 0, that means the
    // Client didn't give us a price, so we'll be getting current quotes instead.
    const bool should_get_market_price = request.price < 0;

    const string symbol = OrderSymbol();
    double       price  = request.price;

    bool order_close_succeeded = false;

    for (uint i = 1; i <= tries; i++)
    {
        if (should_get_market_price)
        {
            Tick last_tick;

            // If we failed to get price, try again in the next retries.
            if (!Tick::current(symbol, last_tick))
                continue;

            // Buy orders are closed on bid price; sell orders are closed on ask price.
            switch (optype)
            {
                case OP_BUY:  price = last_tick.bid(); break;
                case OP_SELL: price = last_tick.ask(); break;
            }
        }

        if (OrderClose(request.ticket, lots, price, request.slippage))
        {
            order_close_succeeded = true;
            break;
        }

        const int last_error = GetLastError();

        switch (last_error)
        {
            case ERR_REQUOTE:
            case ERR_PRICE_CHANGED:
            case ERR_OFF_QUOTES:
                continue;

            default:
                return last_error;
        }
    }

    if (!order_close_succeeded)
        return GetLastError();

    if (OrderSelect(request.ticket, SELECT_BY_TICKET))
    {
        response.close_price = OrderClosePrice();
        response.close_time  = OrderCloseTime();
        response.lots        = OrderLots();
        response.comment     = OrderComment();
        response.commission  = OrderCommission();
        response.profit      = OrderProfit();
        response.swap        = OrderSwap();
    }

    response.new_order_ticket = CloseOrderResponse::NO_NEW_ORDER;

    if (is_partial_close)
    {
        tickets.remove(request.ticket);

        const int orders_count = OrdersTotal();

        // Iterate through all open orders to find the remaining order's ticket.
        for (int i = 0; i < orders_count; i++)
        {
            if (!OrderSelect(i, SELECT_BY_POS))
                continue;
            
            if (!tickets.contains(OrderTicket()))
            {
                response.new_order_ticket       = OrderTicket();
                response.new_order_lots         = OrderLots();
                response.new_order_magic_number = OrderMagicNumber();
                response.new_order_comment      = OrderComment();
                response.new_order_commission   = OrderCommission();
                response.new_order_profit       = OrderProfit();
                response.new_order_swap         = OrderSwap();

                break;
            }
        }

        // If control reaches here, that means a partial order was closed, but
        // we were unable to get the remaining order's ticket, likely due to a
        // failure of `OrderSelect()`. In that case, just fallthrough and return
        // a success result, since the order was effectively partially closed.
    }

    return CommandResult::SUCCESS;
}

CommandResult CommandExecutor::execute(const ModifyOrderRequest& request) override
{
    if (!OrderSelect(request.ticket, SELECT_BY_TICKET))
        return GetLastError();

    double   price      = request.price;
    datetime expiration = request.expiration;

    switch (OrderType())
    {
        case OP_BUY:
        case OP_SELL:
            break;
        
        default:
            if (price < 0)
                price = OrderOpenPrice();
            
            if (expiration == 0)
                expiration = OrderExpiration();
    }

    if (!OrderModify(request.ticket, price, request.stop_loss, request.take_profit, expiration))
    {
        const int last_error = GetLastError();

        // `ERR_NO_RESULT` means nothing changed because the given values
        // are identical to the current ones, so consider this a success.
        if (last_error != ERR_NO_RESULT)
            return last_error;
    }

    return CommandResult::SUCCESS;
}
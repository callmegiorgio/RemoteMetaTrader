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
    CommandResult execute(const GetCurrentBarRequest& request, GetCurrentBarResponse& response) override;
    CommandResult execute(const GetHistoryBarsRequest& request, GetHistoryBarsResponse& response) override;
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

CommandResult CommandExecutor::execute(const GetCurrentBarRequest& request, GetCurrentBarResponse& response) override
{
    ResetLastError();

    response.time   = iTime  (request.symbol, request.timeframe, 0);
    response.open   = iOpen  (request.symbol, request.timeframe, 0);
    response.high   = iHigh  (request.symbol, request.timeframe, 0);
    response.low    = iLow   (request.symbol, request.timeframe, 0);
    response.close  = iClose (request.symbol, request.timeframe, 0);
    response.volume = iVolume(request.symbol, request.timeframe, 0);

    return GetLastError();
}

CommandResult CommandExecutor::execute(const GetHistoryBarsRequest& request, GetHistoryBarsResponse& response) override
{
    const datetime start_time = request.start_time.value_or(0);
    datetime end_time;

    if (!request.end_time.get(end_time))
    {
        // According to the MQL4 documentation, this is the last valid date
        // for `datetime`.
        // TODO: move this to a function of its own?
        MqlDateTime dt;
        dt.year = 3000;
        dt.mon  = 12;
        dt.day  = 31;
        dt.hour = 00;
        dt.min  = 00;
        dt.sec  = 00;

        end_time = StructToTime(dt);
    }

    response.rates_count =
        CopyRates(
            request.symbol,
            request.timeframe,
            start_time,
            end_time,
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
    const bool should_get_market_price = (request.price.has_value() == false);

    const int      slippage     = request.slippage.value_or(0);
    const double   stop_loss    = request.stop_loss.value_or(0);
    const double   take_profit  = request.take_profit.value_or(0);
    const string   comment      = request.comment.value_or("");
    const int      magic_number = request.magic_number.value_or(0);
    const datetime expiration   = request.expiration.value_or(0);

    double price = request.price.value_or(0);

    CommandResult cmd_result = CommandResult::SUCCESS;

    for (uint i = 1; i <= tries; i++)
    {
        if (should_get_market_price)
        {
            Tick last_tick;

            // If we failed to get price, try again in the next retries.
            if (!Tick::current(request.symbol, last_tick))
            {
                cmd_result = GetLastError();
                continue;
            }

            // We can only use the current market price to fill a market order.
            // If the Client asked us to place a pending order, the Client had
            // to provide the price, because it doesn't make sense to place
            // pending orders on current price.
            // TODO: get minimum/maximum opening price for pending orders.
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
                slippage,
                stop_loss,
                take_profit,
                comment,
                magic_number,
                expiration
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

            cmd_result = CommandResult::SUCCESS;
            break;
        }

        cmd_result = GetLastError();

        switch (cmd_result.code())
        {
            case ERR_REQUOTE:
            case ERR_PRICE_CHANGED:
            case ERR_OFF_QUOTES:
                continue;

            default:
                break;
        }
    }

    return cmd_result;
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

    const double lots             = request.lots.value_or(OrderLots());
    const bool   is_partial_close = lots < OrderLots();

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
    // given to us by the Client.
    const bool should_get_market_price = (request.price.has_value() == false);

    const string symbol   = OrderSymbol();
    const int    slippage = request.slippage.value_or(0);
    double       price    = request.price.value_or(0);
    
    CommandResult cmd_result;

    for (uint i = 1; i <= tries; i++)
    {
        if (should_get_market_price)
        {
            Tick last_tick;

            // If we failed to get price, try again in the next retries.
            if (!Tick::current(symbol, last_tick))
            {
                cmd_result = GetLastError();
                continue;
            }

            // Buy orders are closed on bid price; sell orders are closed on ask price.
            switch (optype)
            {
                case OP_BUY:  price = last_tick.bid(); break;
                case OP_SELL: price = last_tick.ask(); break;
            }
        }

        if (OrderClose(request.ticket, lots, price, slippage))
        {
            cmd_result = CommandResult::SUCCESS;
            break;
        }

        cmd_result = GetLastError();

        switch (cmd_result.code())
        {
            case ERR_REQUOTE:
            case ERR_PRICE_CHANGED:
            case ERR_OFF_QUOTES:
                continue;

            default:
                break;
        }
    }

    if (cmd_result.code() != CommandResult::SUCCESS)
        return cmd_result;

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
                CloseOrderResponseNewOrder new_order;

                new_order.ticket       = OrderTicket();
                new_order.lots         = OrderLots();
                new_order.magic_number = OrderMagicNumber();
                new_order.comment      = OrderComment();
                new_order.commission   = OrderCommission();
                new_order.profit       = OrderProfit();
                new_order.swap         = OrderSwap();

                response.new_order = new_order;

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

    double   price      = 0;
    datetime expiration = 0;

    switch (OrderType())
    {
        case OP_BUY:
        case OP_SELL:
            // If neither S/L or T/P is provided in the request for a filled order,
            // then, welp, there's nothing to change about it.
            if (!request.stop_loss.has_value() && !request.take_profit.has_value())
                return CommandResult::SUCCESS;

            break;
        
        default:
            // If it is a pending order, try reading an open price or expiration time,
            // or use their current values instead.
            price      = request.price.value_or(OrderOpenPrice());
            expiration = request.expiration.value_or(OrderExpiration());
    }

    const double stop_loss   = request.stop_loss.value_or(OrderStopLoss());
    const double take_profit = request.take_profit.value_or(OrderTakeProfit());

    if (!OrderModify(request.ticket, price, stop_loss, take_profit, expiration))
    {
        const int last_error = GetLastError();

        // `ERR_NO_RESULT` means nothing changed because the given values
        // are identical to the current ones, so consider this a success.
        if (last_error != ERR_NO_RESULT)
            return last_error;
    }

    return CommandResult::SUCCESS;
}
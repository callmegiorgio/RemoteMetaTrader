#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>
#include <Mql/Collection/ArraySet.mqh>

// Local
#include "../Trading/Order.mqh"
#include "../Utility/Observer.mqh"
#include "OrderFinishedEvent.mqh"
#include "OrderModifiedEvent.mqh"
#include "OrderPlacedEvent.mqh"
#include "OrderUpdatedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Notifies changes in the state of active orders.
///
/// The class `OrderEventSubject` keeps track of *active* orders, that is,
/// orders in the MQL trade pool that are either pending or filled. Every time
/// a change in the state of any of such orders occurs, a call to `update()`
/// will notify it to observers previously registered to its subject.
///
////////////////////////////////////////////////////////////////////////////////
class OrderEventSubject {
public:
    OrderEventSubject();
    ~OrderEventSubject();

    void register(Observer<OrderPlacedEvent>* observer);
    void register(Observer<OrderFinishedEvent>* observer);
    void register(Observer<OrderModifiedEvent>* observer);
    void register(Observer<OrderUpdatedEvent>* observer);

    void update();

private:
    void create_order_and_notify(int ticket);
    void update_order_and_notify(int ticket, Order& order);
    void remove_order_and_notify(int ticket, Order* order);

    HashMap<int, Order*> m_active_orders;

    Subject<OrderPlacedEvent>   m_order_placed_sub;
    Subject<OrderFinishedEvent> m_order_finished_sub;
    Subject<OrderModifiedEvent> m_order_modified_sub;
    Subject<OrderUpdatedEvent>  m_order_updated_sub;
};

//===========================================================================
// --- OrderEventSubject implementation ---
//===========================================================================
OrderEventSubject::OrderEventSubject()
{
    const int order_count = OrdersTotal();

    for (int i = 0; i < order_count; i++)
    {
        if (!OrderSelect(i, SELECT_BY_POS))
            continue;

        Order* order = new Order;
        order.refresh();

        m_active_orders.set(OrderTicket(), order);
    }
}

OrderEventSubject::~OrderEventSubject()
{
    foreachm(int, ticket, Order*, order, m_active_orders)
        delete order;
}

void OrderEventSubject::register(Observer<OrderPlacedEvent>* observer)
{
    m_order_placed_sub.register(observer);
}

void OrderEventSubject::register(Observer<OrderFinishedEvent>* observer)
{
    m_order_finished_sub.register(observer);
}

void OrderEventSubject::register(Observer<OrderModifiedEvent>* observer)
{
    m_order_modified_sub.register(observer);
}

void OrderEventSubject::register(Observer<OrderUpdatedEvent>* observer)
{
    m_order_updated_sub.register(observer);
}

void OrderEventSubject::update()
{
    ArraySet<int> pool_orders;

    const int order_count = OrdersTotal();

    for (int i = 0; i < order_count; i++)
    {
        if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
            pool_orders.add(OrderTicket());
    }

    foreachm(int, ticket, Order*, order, m_active_orders)
    {
        // If we are tracking an order which is still in the trade pool,
        // update it. Otherwise, if the trade pool does not have the order
        // anymore, that means the order has been moved to the history pool.
        if (pool_orders.contains(ticket))
        {
            update_order_and_notify(ticket, order);
            pool_orders.remove(ticket);
        }
        else
        {
            remove_order_and_notify(ticket, order);
        }
    }

    // If there's any order in the trade pool which we are not tracking, that
    // means an order was placed.
    for (Iter<int> it(pool_orders); !it.end(); it.next())
    {
        const int ticket = it.current();
        create_order_and_notify(ticket);
    }
}

void OrderEventSubject::create_order_and_notify(int ticket)
{
    if (!OrderSelect(ticket, SELECT_BY_TICKET))
        return;

    Order* order = new Order;
    order.refresh();

    m_active_orders.set(ticket, order);

    OrderPlacedEvent ev;
    ev.ticket = ticket;
    ev.order  = GetPointer(order);

    m_order_placed_sub.notify(ev);
}

void OrderEventSubject::update_order_and_notify(int ticket, Order& order)
{
    if (!OrderSelect(ticket, SELECT_BY_TICKET))
        return;

    const bool has_been_modified = (
        order.take_profit != OrderTakeProfit() ||
        order.stop_loss   != OrderStopLoss()   ||
        order.open_price  != OrderOpenPrice()  ||
        order.expiration  != OrderExpiration()
    );
    
    // Only possible if order was previously pending.
    const bool has_been_filled = (order.type != OrderType());

    const bool has_been_updated = (
        order.comment    != OrderComment()    ||
        order.commission != OrderCommission() ||
        order.profit     != OrderProfit()     ||
        order.swap       != OrderSwap()
    );
    
    if (!(has_been_modified || has_been_filled || has_been_updated))
        return;

    order.refresh();

    if (has_been_modified)
    {
        OrderModifiedEvent ev;
        ev.ticket = ticket;
        ev.order  = GetPointer(order);

        m_order_modified_sub.notify(ev);
    }

    if (has_been_filled)
    {
        OrderPlacedEvent ev;
        ev.ticket = ticket;
        ev.order  = GetPointer(order);

        m_order_placed_sub.notify(ev);
    }

    if (has_been_updated)
    {
        OrderUpdatedEvent ev;
        ev.ticket = ticket;
        ev.order  = GetPointer(order);

        m_order_updated_sub.notify(ev);
    }
}

void OrderEventSubject::remove_order_and_notify(int ticket, Order* order)
{
    if (!OrderSelect(ticket, SELECT_BY_TICKET))
        return;

    m_active_orders.remove(ticket);

    order.refresh();

    OrderFinishedEvent ev;
    ev.ticket = ticket;
    ev.order  = order;
    
    m_order_finished_sub.notify(ev);

    delete order;
}
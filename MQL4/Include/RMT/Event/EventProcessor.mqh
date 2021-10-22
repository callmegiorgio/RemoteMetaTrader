#property strict

// Local
#include "AccountEventSubject.mqh"
#include "AccountChangedEventPublisher.mqh"
#include "BarClosedEventPublisher.mqh"
#include "EquityUpdatedEventPublisher.mqh"
#include "InstrumentEventSubject.mqh"
#include "OrderEventSubject.mqh"
#include "OrderFinishedEventPublisher.mqh"
#include "OrderModifiedEventPublisher.mqh"
#include "OrderPlacedEventPublisher.mqh"
#include "OrderUpdatedEventPublisher.mqh"
#include "TickEventPublisher.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Updates event subjects.
///
/// The class `EventProcessor` provides a thin abstraction to the process of
/// notifying events by gathering event subjects together.
///
/// A call to `process_events()` will cause the event subjects stored by the
/// class to be updated, which in turn may cause events to be fired and event
/// observers to be called.
///
////////////////////////////////////////////////////////////////////////////////
class EventProcessor {
public:
    EventProcessor(Server& the_server);

    void process_events();

    AccountEventSubject* account_event_subject();
    InstrumentEventSubject* instrument_event_subject();
    OrderEventSubject* order_event_subject();

private:
    AccountEventSubject    m_account_ev_sub;
    InstrumentEventSubject m_instrument_ev_sub;
    OrderEventSubject      m_order_ev_sub;
};

//===========================================================================
// --- EventProcessor implementation ---
//===========================================================================
EventProcessor::EventProcessor(Server& the_server)
{
    m_account_ev_sub.register(new AccountChangedEventPublisher(the_server));
    m_account_ev_sub.register(new EquityUpdatedEventPublisher(the_server));
    m_instrument_ev_sub.register(new TickEventPublisher(the_server));
    m_instrument_ev_sub.register(new BarClosedEventPublisher(the_server));
    m_order_ev_sub.register(new OrderPlacedEventPublisher(the_server));
    m_order_ev_sub.register(new OrderFinishedEventPublisher(the_server));
    m_order_ev_sub.register(new OrderModifiedEventPublisher(the_server));
    m_order_ev_sub.register(new OrderUpdatedEventPublisher(the_server));
}

void EventProcessor::process_events()
{
    m_instrument_ev_sub.update();
    m_order_ev_sub.update();
    m_account_ev_sub.update();
}

AccountEventSubject* EventProcessor::account_event_subject()
{
    return GetPointer(m_account_ev_sub);
}

InstrumentEventSubject* EventProcessor::instrument_event_subject()
{
    return GetPointer(m_instrument_ev_sub);
}

OrderEventSubject* EventProcessor::order_event_subject()
{
    return GetPointer(m_order_ev_sub);
}
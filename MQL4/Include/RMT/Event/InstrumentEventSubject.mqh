#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "../Trading/Tick.mqh"
#include "../Utility/DateTime.mqh"
#include "../Utility/Observer.mqh"
#include "TickEvent.mqh"
#include "BarClosedEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Notifies receipt of quotes for subscribed instruments.
///
/// The class `InstrumentEventSubject` allows subscription to instruments available in
/// the trade server. For each subscribed instrument, a call to `update()` will
/// verify if that instrument has a new quote, and if yes, the new quote will be
/// delivered to registered observers as a `TickEvent`.
///
////////////////////////////////////////////////////////////////////////////////
class InstrumentEventSubject {
public:
    InstrumentEventSubject();
    ~InstrumentEventSubject();

    void register(Observer<TickEvent>* observer);
    void register(Observer<BarClosedEvent>* observer);

    void subscribe(string symbol);
    void unsubscribe(string symbol);

    void subscribe_all();
    void unsubscribe_all();
    
    int count() const;
    bool is_subscribed(string symbol) const;

    void update();

private:
    HashMap<string, Tick*> m_ticks;

    Subject<TickEvent>      m_tick_ev_sub;
    Subject<BarClosedEvent> m_bar_closed_ev_sub;
};

//===========================================================================
// --- InstrumentEventSubject implementation ---
//===========================================================================
InstrumentEventSubject::InstrumentEventSubject()
{}

InstrumentEventSubject::~InstrumentEventSubject()
{
    unsubscribe_all();
}

void InstrumentEventSubject::register(Observer<TickEvent>* observer)
{
    m_tick_ev_sub.register(observer);
}

void InstrumentEventSubject::register(Observer<BarClosedEvent>* observer)
{
    m_bar_closed_ev_sub.register(observer);
}

void InstrumentEventSubject::subscribe(string symbol)
{
    Tick* tick = m_ticks.get(symbol, NULL);

    if (tick == NULL)
        m_ticks.set(symbol, new Tick);
}

void InstrumentEventSubject::unsubscribe(string symbol)
{
    Tick* tick = m_ticks.get(symbol, NULL);

    if (tick != NULL)
    {
        delete tick;
        m_ticks.remove(symbol);
    }
}

void InstrumentEventSubject::subscribe_all()
{
    const int n = SymbolsTotal(false);
                
    for (int i = 0; i < n; i++)
        subscribe(SymbolName(i, false));
}

void InstrumentEventSubject::unsubscribe_all()
{
    foreachm(string, symbol, Tick*, tick, m_ticks)
        delete tick;
    
    m_ticks.clear();
}

int InstrumentEventSubject::count() const
{
    return m_ticks.size();
}

bool InstrumentEventSubject::is_subscribed(string symbol) const
{
    return m_ticks.contains(symbol);
}

void InstrumentEventSubject::update()
{
    Tick last_tick;
    
    foreachm(string, symbol, Tick*, tick, m_ticks)
    {
        if (!Tick::current(symbol, last_tick))
            continue;

        if (tick.bid() == last_tick.bid() && tick.ask() == last_tick.ask())
            continue;
        
        const DateTime current_tick_time = tick.server_time();
        const DateTime previous_tick_time = last_tick.server_time();

        tick = last_tick;

        if (current_tick_time.minute() != previous_tick_time.minute())
        {
            BarClosedEvent bar_closed_ev;
            bar_closed_ev.symbol = symbol;
            
            if (Bar::at(symbol, PERIOD_M1, 1, bar_closed_ev.bar))
                m_bar_closed_ev_sub.notify(bar_closed_ev);
        }

        TickEvent tick_ev;
        tick_ev.symbol = symbol;
        tick_ev.tick   = last_tick;

        m_tick_ev_sub.notify(tick_ev);
    }
}
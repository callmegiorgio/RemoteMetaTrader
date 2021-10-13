#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "../Trading/Tick.mqh"
#include "../Utility/Observer.mqh"
#include "TickEvent.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Notifies receipt of quotes for subscribed instruments.
///
/// The class `TickEventSubject` allows subscription to instruments available in
/// the trade server. For each subscribed instrument, a call to `update()` will
/// verify if that instrument has a new quote, and if yes, the new quote will be
/// delivered to registered observers as a `TickEvent`.
///
////////////////////////////////////////////////////////////////////////////////
/// Stores symbols which a client is subscribed to.
class TickEventSubject : public Subject<TickEvent> {
public:
    TickEventSubject();
    ~TickEventSubject();

    void subscribe(string symbol);
    void unsubscribe(string symbol);

    void subscribe_all();
    void unsubscribe_all();
    
    int count() const;
    bool is_subscribed(string symbol) const;

    void update();

private:
    HashMap<string, Tick*> m_ticks;
};

//===========================================================================
// --- TickEventSubject implementation ---
//===========================================================================
TickEventSubject::TickEventSubject()
{}

TickEventSubject::~TickEventSubject()
{
    unsubscribe_all();
}

void TickEventSubject::subscribe(string symbol)
{
    Tick* tick = m_ticks.get(symbol, NULL);

    if (tick == NULL)
        m_ticks.set(symbol, new Tick);
}

void TickEventSubject::unsubscribe(string symbol)
{
    Tick* tick = m_ticks.get(symbol, NULL);

    if (tick != NULL)
    {
        delete tick;
        m_ticks.remove(symbol);
    }
}

void TickEventSubject::subscribe_all()
{
    const int n = SymbolsTotal(false);
                
    for (int i = 0; i < n; i++)
        subscribe(SymbolName(i, false));
}

void TickEventSubject::unsubscribe_all()
{
    foreachm(string, symbol, Tick*, tick, m_ticks)
        delete tick;
    
    m_ticks.clear();
}

int TickEventSubject::count() const
{
    return m_ticks.size();
}

bool TickEventSubject::is_subscribed(string symbol) const
{
    return m_ticks.contains(symbol);
}

void TickEventSubject::update()
{
    Tick last_tick;
    
    foreachm(string, symbol, Tick*, tick, m_ticks)
    {
        if (!Tick::current(symbol, last_tick))
            continue;

        if (tick.bid() == last_tick.bid() && tick.ask() == last_tick.ask())
            continue;

        tick = last_tick;
        
        TickEvent ev;
        ev.symbol = symbol;
        ev.tick   = last_tick;

        notify(ev);
    }
}
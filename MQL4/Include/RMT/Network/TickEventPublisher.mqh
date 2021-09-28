#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "../Protocol/Event/TickEvent.mqh"
#include "../Trading/Tick.mqh"
#include "EventPublisher.mqh"
#include "Server.mqh"

/// Stores symbols which a client is subscribed to.
class TickEventPublisher : private EventPublisher {
public:
    TickEventPublisher(Server& the_server);
    ~TickEventPublisher();

    void insert(string symbol);
    void remove(string symbol);

    void fill();
    void clear();
    
    int size() const;
    bool contains(string symbol) const;

    void process_events() override;

private:
    HashMap<string, Tick*> m_ticks;
};

//===========================================================================
// --- TickEventPublisher implementation ---
//===========================================================================
TickEventPublisher::TickEventPublisher(Server& the_server)
    : EventPublisher(the_server)
{}

TickEventPublisher::~TickEventPublisher()
{
    clear();
}

void TickEventPublisher::insert(string symbol)
{
    Tick* tick = m_ticks.get(symbol, NULL);

    if (tick == NULL)
        m_ticks.set(symbol, new Tick);
}

void TickEventPublisher::remove(string symbol)
{
    Tick* tick = m_ticks.get(symbol, NULL);

    if (tick != NULL)
    {
        delete tick;
        m_ticks.remove(symbol);
    }
}

void TickEventPublisher::fill()
{
    const int n = SymbolsTotal(false);
                
    for (int i = 0; i < n; i++)
        insert(SymbolName(i, false));
}

void TickEventPublisher::clear()
{
    foreachm(string, symbol, Tick*, tick, m_ticks)
        delete tick;
}

int TickEventPublisher::size() const
{
    return m_ticks.size();
}

bool TickEventPublisher::contains(string symbol) const
{
    return m_ticks.contains(symbol);
}

void TickEventPublisher::process_events()
{
    Tick last_tick;
    
    foreachm(string, symbol, Tick*, tick, m_ticks)
    {
        if (!Tick::current(symbol, last_tick))
            continue;

        // if (!SymbolSelect(symbol, true))
        //     continue;

        // if (!SymbolInfoTick(symbol, last_tick))
        //     continue;
        
        // if (last_tick.time == tick.server_time && 
        //     last_tick.bid  == tick.bid &&
        //     last_tick.ask  == tick.ask)
        //     continue;
        
        TickEvent ev;
        ev.symbol = symbol;
        ev.tick   = last_tick;

        publish(ev);

        tick = last_tick;
    }
}
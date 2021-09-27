#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "Protocol/Event/TickEvent.mqh"
#include "EventPublisher.mqh"
#include "Server.mqh"

class Tick {
public:
    datetime server_time;
    double bid;
    double ask;
};

/// Stores symbols which a client is subscribed to.
class TickEventWatcher : private EventPublisher {
public:
    TickEventWatcher(Server& the_server);
    ~TickEventWatcher();

    void insert(string symbol);
    void remove(string symbol);

    void fill();
    void clear();
    
    int size() const;
    bool contains(string symbol) const;

    void process_events();

private:
    HashMap<string, Tick*> m_ticks;
};

//===========================================================================
// --- TickEventWatcher implementation ---
//===========================================================================
TickEventWatcher::TickEventWatcher(Server& the_server)
    : EventPublisher(the_server)
{}

TickEventWatcher::~TickEventWatcher()
{
    clear();
}

void TickEventWatcher::insert(string symbol)
{
    Tick* tick = m_ticks.get(symbol, NULL);

    if (tick != NULL)
        return;

    tick = new Tick;
    tick.server_time = datetime(0);
    tick.bid         = double(0);
    tick.ask         = double(0);

    m_ticks.set(symbol, tick);
}

void TickEventWatcher::remove(string symbol)
{
    Tick* tick = m_ticks.get(symbol, NULL);

    if (tick != NULL)
    {
        delete tick;
        m_ticks.remove(symbol);
    }
}

void TickEventWatcher::fill()
{
    const int n = SymbolsTotal(false);
                
    for (int i = 0; i < n; i++)
        insert(SymbolName(i, false));
}

void TickEventWatcher::clear()
{
    foreachm(string, symbol, Tick*, tick, m_ticks)
        delete tick;
}

int TickEventWatcher::size() const
{
    return m_ticks.size();
}

bool TickEventWatcher::contains(string symbol) const
{
    return m_ticks.contains(symbol);
}

void TickEventWatcher::process_events()
{
    MqlTick last_tick;
    
    foreachm(string, symbol, Tick*, tick, m_ticks)
    {
        if (!SymbolSelect(symbol, true))
            continue;

        if (!SymbolInfoTick(symbol, last_tick))
            continue;
        
        if (last_tick.time == tick.server_time && 
            last_tick.bid  == tick.bid &&
            last_tick.ask  == tick.ask)
            continue;
        
        TickEvent ev;
        ev.symbol = symbol;
        ev.tick   = last_tick;

        if (publish(ev))
        {
            tick.server_time = last_tick.time;
            tick.bid         = last_tick.bid;
            tick.ask         = last_tick.ask;
        }
    }
}
#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

// Local
#include "Protocol/Event/TickEvent.mqh"
#include "EventPublisher.mqh"
#include "Server.mqh"

/// Stores symbols which a client is subscribed to.
class TickEventWatcher : private EventPublisher {
public:
    TickEventWatcher(Server& the_server);

    void insert(string symbol);
    void remove(string symbol);

    void fill();
    void clear();
    
    int size() const;
    bool contains(string symbol) const;

    void process_events();

private:
    HashMap<string, datetime> m_timestamps;
};

//===========================================================================
// --- TickEventWatcher implementation ---
//===========================================================================
TickEventWatcher::TickEventWatcher(Server& the_server)
    : EventPublisher(the_server)
{}

void TickEventWatcher::insert(string symbol)
{
    m_timestamps.set(symbol, m_timestamps.get(symbol, 0));
}

void TickEventWatcher::remove(string symbol)
{
    m_timestamps.remove(symbol);
}

void TickEventWatcher::fill()
{
    const int n = SymbolsTotal(false);
                
    for (int i = 0; i < n; i++)
        insert(SymbolName(i, false));
}

void TickEventWatcher::clear()
{
    m_timestamps.clear();
}

int TickEventWatcher::size() const
{
    return m_timestamps.size();
}

bool TickEventWatcher::contains(string symbol) const
{
    return m_timestamps.contains(symbol);
}

void TickEventWatcher::process_events()
{
    MqlTick last_tick;
    
    foreachm(string, symbol, datetime, timestamp, m_timestamps)
    {
        if (!SymbolSelect(symbol, true))
            continue;

        if (!SymbolInfoTick(symbol, last_tick))
            continue;
        
        if (last_tick.time == timestamp)
            continue;
        
        TickEvent ev;
        ev.symbol = symbol;
        ev.tick   = last_tick;

        if (publish(ev))
            m_timestamps.set(symbol, last_tick.time);
    }
}
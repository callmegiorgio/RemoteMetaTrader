#property strict

// 3rdparty
#include <Mql/Collection/HashMap.mqh>

struct SymbolTick {
    string symbol;
    MqlTick mql_tick;
};

/// Stores symbols which a client is subscribed to.
class SymbolWatcher {
public:
    static SymbolWatcher* instance();

    void insert(string symbol);
    void remove(string symbol);

    void fill();
    void clear();
    
    int size() const;
    bool contains(string symbol) const;
    
    int get_ticks(SymbolTick& ticks[]);

private:
    static SymbolWatcher s_instance;

    HashMap<string, datetime> m_timestamps;
};

//===========================================================================
// --- SymbolWatcher implementation ---
//===========================================================================
SymbolWatcher SymbolWatcher::s_instance;

static SymbolWatcher* SymbolWatcher::instance()
{
    return GetPointer(SymbolWatcher::s_instance);
}

void SymbolWatcher::insert(string symbol)
{
    m_timestamps.set(symbol, m_timestamps.get(symbol, 0));
}

void SymbolWatcher::remove(string symbol)
{
    m_timestamps.remove(symbol);
}

void SymbolWatcher::fill()
{
    const int n = SymbolsTotal(false);
                
    for (int i = 0; i < n; i++)
        insert(SymbolName(i, false));
}

void SymbolWatcher::clear()
{
    m_timestamps.clear();
}

int SymbolWatcher::size() const
{
    return m_timestamps.size();
}

bool SymbolWatcher::contains(string symbol) const
{
    return m_timestamps.contains(symbol);
}

int SymbolWatcher::get_ticks(SymbolTick& ticks[])
{
    int ticks_count = ArraySize(ticks);
    MqlTick last_tick;
    
    foreachm(string, symbol, datetime, timestamp, m_timestamps)
    {
        if (SymbolInfoTick(symbol, last_tick) && last_tick.time != timestamp)
        {
            m_timestamps.set(symbol, last_tick.time);
            
            ticks_count++;
                       
            if (ArrayResize(ticks, ticks_count) != ticks_count)
                break;
            
            ticks[ticks_count - 1].symbol   = symbol;
            ticks[ticks_count - 1].mql_tick = last_tick;
        }
    }
    
    return ticks_count;
}
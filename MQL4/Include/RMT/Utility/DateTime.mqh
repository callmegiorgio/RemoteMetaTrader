#property strict

// Local
#include "Time.mqh"

class DateTime {
public:
    static DateTime min();
    static DateTime max();

    DateTime(datetime timestamp = 0);
    DateTime(const DateTime& other);

    datetime timestamp() const;

    uint year() const;
    uint month() const;
    uint day() const;
    uint hour() const;
    uint minute() const;
    uint second() const;

    Time time() const;

    DateTime* operator=(const DateTime& other);
    
    bool operator==(const DateTime& other) const;
    bool operator!=(const DateTime& other) const;
    bool operator>(const DateTime& other) const;
    bool operator>=(const DateTime& other) const;
    bool operator<(const DateTime& other) const;
    bool operator<=(const DateTime& other) const;

private:
    datetime m_timestamp;
};

//===========================================================================
// --- DateTime implementation ---
//===========================================================================
static DateTime DateTime::min()
{
    return DateTime(0);
}

static DateTime DateTime::max()
{
    MqlDateTime dt;
    dt.year = 3000;
    dt.mon  = 12;
    dt.day  = 31;
    dt.hour = 00;
    dt.min  = 00;
    dt.sec  = 00;

    return StructToTime(dt);
}

DateTime::DateTime(datetime timestamp)
{
    m_timestamp = timestamp;
}

DateTime::DateTime(const DateTime& other)
{
    this.operator=(other);
}

datetime DateTime::timestamp() const
{
    return m_timestamp;
}

uint DateTime::year() const
{
    return TimeYear(m_timestamp);
}

uint DateTime::month() const
{
    return TimeMonth(m_timestamp);
}

uint DateTime::day() const
{
    return TimeDay(m_timestamp);
}

uint DateTime::hour() const
{
    return TimeHour(m_timestamp);
}

uint DateTime::minute() const
{
    return TimeMinute(m_timestamp);
}

uint DateTime::second() const
{
    return TimeSeconds(m_timestamp);
}

Time DateTime::time() const
{
    return Time(hour(), minute(), second());
}

DateTime* DateTime::operator=(const DateTime& other)
{
    m_timestamp = other.m_timestamp;

    return GetPointer(this);
}

bool DateTime::operator==(const DateTime& other) const
{
    return m_timestamp == other.m_timestamp;
}

bool DateTime::operator!=(const DateTime& other) const
{
    return m_timestamp != other.m_timestamp;
}

bool DateTime::operator>(const DateTime& other) const
{
    return m_timestamp > other.m_timestamp;
}

bool DateTime::operator>=(const DateTime& other) const
{
    return m_timestamp >= other.m_timestamp;
}

bool DateTime::operator<(const DateTime& other) const
{
    return m_timestamp < other.m_timestamp;
}

bool DateTime::operator<=(const DateTime& other) const
{
    return m_timestamp <= other.m_timestamp;
}
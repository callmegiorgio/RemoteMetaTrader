#property strict

class Time {
public:
    static Time now();

    Time(uint hour = 0, uint minute = 0, uint second = 0);
    Time(const Time& other);

    uint hour() const;
    uint minute() const;
    uint second() const;

    /// Returns the string representation of the time, formatted as "hh:mi:ss".
    string str() const;

    Time* operator=(const Time& other);

    /// Equality compares two times.
    /// @{
    bool operator==(const Time& other) const;
    bool operator!=(const Time& other) const;
    bool operator> (const Time& other) const;
    bool operator>=(const Time& other) const;
    bool operator< (const Time& other) const;
    bool operator<=(const Time& other) const;
    /// @}

private:
    uint m_seconds;
};

static Time Time::now()
{
    return Time(
        uint(Hour()),
        uint(Minute()),
        uint(Seconds())
    );
}

Time::Time(uint hour, uint minute, uint second)
{
    m_seconds = (hour * 3600) + (minute * 60) + second;
}

Time::Time(const Time& other)
{
    m_seconds = other.m_seconds;
}

uint Time::hour() const
{
    return m_seconds / 3600;
}

uint Time::minute() const
{
    return (m_seconds - (hour() * 3600)) / 60;
}

uint Time::second() const
{
    return m_seconds - (hour() * 3600) - (minute() * 60);
}

string Time::str() const
{
    return StringFormat("%02d:%02d:%02d", hour(), minute(), second());
}

Time* Time::operator=(const Time& other)
{
    m_seconds = other.m_seconds;
    
    return GetPointer(this);
}

bool Time::operator==(const Time& other) const
{
    return m_seconds == other.m_seconds;
}

bool Time::operator!=(const Time& other) const
{
    return m_seconds != other.m_seconds;
}

bool Time::operator>(const Time& other) const
{
    return m_seconds > other.m_seconds;
}

bool Time::operator>=(const Time& other) const
{
    return m_seconds >= other.m_seconds;
}

bool Time::operator<(const Time& other) const
{
    return m_seconds < other.m_seconds;
}

bool Time::operator<=(const Time& other) const
{
    return m_seconds <= other.m_seconds;
}
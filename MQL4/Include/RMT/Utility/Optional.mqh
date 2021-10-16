#property strict

template <typename T>
class Optional {
public:
    Optional();
    Optional(T value);
    Optional(const Optional& other);

    bool get(T& value) const;
    T value_or(T fallback) const;

    void reset();

    bool has_value() const;

    Optional* operator=(T value);
    Optional* operator=(const Optional& other);

private:
    T m_value[];
};

template <typename T>
class OptionalComplex {
public:
    OptionalComplex();
    OptionalComplex(const T& value);
    OptionalComplex(const OptionalComplex& other);
    ~OptionalComplex();

    bool get(T& value) const;
    T* value_or(T* fallback) const;
    T* value() const;

    void reset();

    bool has_value() const;

    OptionalComplex* operator=(const T& value);
    OptionalComplex* operator=(const OptionalComplex& other);

private:
    T* m_value;
};

//===========================================================================
// --- Optional implementation ---
//===========================================================================
template <typename T>
Optional::Optional()
{}

template <typename T>
Optional::Optional(T value)
{
    if (ArrayResize(m_value, 1) == 1)
        m_value[0] = value;
}

template <typename T>
Optional::Optional(const Optional& other)
{
    this.operator=(other);
}

template <typename T>
bool Optional::get(T& value) const
{
    if (!has_value())
        return false;

    value = m_value[0];
    return true;
}

template <typename T>
T Optional::value_or(T fallback) const
{
    T value;

    if (get(value))
        return value;
    
    return fallback;
}

template <typename T>
T Optional::value() const
{
    return value_or(NULL);
}

template <typename T>
void Optional::reset()
{
    ArrayResize(m_value, 0);
}

template <typename T>
bool Optional::has_value() const
{
    return ArraySize(m_value) == 1;
}

template <typename T>
Optional* Optional::operator=(T value)
{
    if (has_value() || ArrayResize(m_value, 1) == 1)
        m_value[0] = value;
    
    return GetPointer(this);
}

template <typename T>
Optional* Optional::operator=(const Optional& other)
{
    ArrayCopy(m_value, other.m_value, 0, 0, ArraySize(other.m_value));

    return GetPointer(this);
}

//===========================================================================
// --- OptionalComplex implementation ---
//===========================================================================
template <typename T>
OptionalComplex::OptionalComplex()
{
    m_value = NULL;
}

template <typename T>
OptionalComplex::OptionalComplex(const T& value)
{
    m_value = new T(value);
}

template <typename T>
OptionalComplex::OptionalComplex(const OptionalComplex& other)
{
    this.operator=(other);
}

template <typename T>
OptionalComplex::~OptionalComplex()
{
    if (m_value != NULL)
        delete m_value;
}

template <typename T>
bool OptionalComplex::get(T& value) const
{
    if (!has_value())
        return false;

    value = m_value;
    return true;
}

template <typename T>
T* OptionalComplex::value_or(T* fallback) const
{
    if (!has_value())
        return m_value;

    return fallback;
}

template <typename T>
T* OptionalComplex::value() const
{
    return m_value;
}

template <typename T>
void OptionalComplex::reset()
{
    if (has_value())
    {
        delete m_value;
        m_value = NULL;
    }
}

template <typename T>
bool OptionalComplex::has_value() const
{
    return m_value != NULL;
}

template <typename T>
OptionalComplex* OptionalComplex::operator=(const T& value)
{
    if (!has_value())
        m_value = new T(value);
    else
        m_value = value;

    return GetPointer(this);
}

template <typename T>
OptionalComplex* OptionalComplex::operator=(const OptionalComplex& other)
{
    if (other.m_value != NULL)
        this.operator=(other.m_value);

    return GetPointer(this);
}
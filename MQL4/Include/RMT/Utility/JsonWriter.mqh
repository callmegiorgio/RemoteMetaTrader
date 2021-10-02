#property strict

// Local
#include "JsonValue.mqh"
#include "Optional.mqh"

class JsonWriter {
public:
    JsonWriter(JsonValue& doc);
    JsonWriter(JsonWriter& other);

    template <typename T>
    void write(const T& obj);

    template <typename T>
    void write(string key, const Optional<T>& opt);

    template <typename T>
    void write(string key, const OptionalComplex<T>& opt);

    template <typename T>
    void write(string key, T value);

    template <typename T>
    void write(int index, const Optional<T>& opt);

    template <typename T>
    void write(int index, const OptionalComplex<T>& opt);

    template <typename T>
    void write(int index, T value);

    JsonWriter subdocument(string key);

    JsonWriter subdocument(int index);

private:
    JsonValue* m_doc;
};

//===========================================================================
// --- JsonWriter implementation ---
//===========================================================================
JsonWriter::JsonWriter(JsonValue& doc)
{
    m_doc = GetPointer(doc);
}

JsonWriter::JsonWriter(JsonWriter& other)
{
    m_doc = other.m_doc;
}

template <typename T>
void JsonWriter::write(const T& obj)
{
    obj.write(this);
}

template <typename T>
void JsonWriter::write(string key, const Optional<T>& opt)
{
    T value;

    if (opt.get(value))
        m_doc[key] = value;
}

template <typename T>
void JsonWriter::write(string key, const OptionalComplex<T>& opt)
{
    T value;

    if (opt.get(value))
        subdocument(key).write(value);
}

template <typename T>
void JsonWriter::write(string key, T value)
{
    m_doc[key] = value;
}

template <typename T>
void JsonWriter::write(int index, const Optional<T>& opt)
{
    T value;

    if (opt.get(value))
        m_doc[index] = value;
}

template <typename T>
void JsonWriter::write(int index, const OptionalComplex<T>& opt)
{
    T value;

    if (opt.get(value))
        subdocument(index).write(value);
}

template <typename T>
void JsonWriter::write(int index, T value)
{
    m_doc[index] = value;
}

JsonWriter JsonWriter::subdocument(string key)
{
    return m_doc[key];
}

JsonWriter JsonWriter::subdocument(int index)
{
    return m_doc[index];
}
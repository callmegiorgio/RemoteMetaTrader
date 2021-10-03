#property strict

// Local
#include "JsonValue.mqh"
#include "Optional.mqh"

/////////////////////////////////////////////////////////////////////////////
/// Reads values from a JSON object or array.
///
/// The class `JsonReader` allows reading values from a JSON object or array,
/// while providing error-handling methods which subclassed may overload.
///
/// The class is based on the notion that a user may want some values in the
/// JSON document or array to be optional, and other values to be required.
///
/// All reading methods (`read_*()`) provided by the class have a parameter
/// `optional`, which defines whether the value to be read is optional. If
/// the reading process fails and `optional` is `true`, no error is raised.
/// Otherwise, if `optional` is `false`, thus making it a required value,
/// one of the error-handling methods, such as `on_missing_key_error()`, is
/// invoked. In any case, the reading method returns `false` as a result of
/// the failed reading attempt.
///
/////////////////////////////////////////////////////////////////////////////
class JsonReader {
public:
    /////////////////////////////////////////////////////////////////////////////
    /// Constructs a reader from a JSON object or array.
    ///
    /// If `value` is not of type `JSON_OBJECT` or `JSON_ARRAY`, all subsequent
    /// calls to any of the reading methods will invoke `on_invalid_type_error()`
    /// and will return `false`.
    ///
    /// @param value A JSON object or array.
    ///
    /////////////////////////////////////////////////////////////////////////////
    JsonReader(const JsonValue* value = NULL);

    void reset(const JsonValue* value = NULL);
    
    /////////////////////////////////////////////////////////////////////////////
    /// Reads a value from the underlying JSON document identified by `key`.
    ///
    /// @param key A string key identifying the value.
    /// @param value A reference variable where a value is read into.
    /// @param optional Whether the value is optional or required.
    /// @return `true` if a value was read into `value`, and `false` otherwise.
    ///
    /// @{
    bool read(string key, string&   value, bool optional);
    bool read(string key, double&   value, bool optional);
    bool read(string key, long&     value, bool optional);
    bool read(string key, int&      value, bool optional);
    bool read(string key, datetime& value, bool optional);
    bool read(string key, bool&     value, bool optional);
    /// @}
    /////////////////////////////////////////////////////////////////////////////

    bool read_at(int index, string&   value, bool optional);
    bool read_at(int index, double&   value, bool optional);
    bool read_at(int index, long&     value, bool optional);
    bool read_at(int index, int&      value, bool optional);
    bool read_at(int index, datetime& value, bool optional);
    bool read_at(int index, bool&     value, bool optional);

    template <typename T>
    bool read_required(string key, T& value);

    template <typename T>
    bool read_optional(string key, Optional<T>& opt);

protected:
    virtual void on_invalid_root_type_error(JsonType actual_type, JsonType expected_type) {}

    /////////////////////////////////////////////////////////////////////////////
    /// Handles a missing-key error.
    ///
    /// This error-handling method is invoked if any of the reading functions
    /// accepting a `key` parameter fails to find a key in the underlying JSON
    /// document.
    ///
    /// @param key A key which is missing from the document.
    ///
    /////////////////////////////////////////////////////////////////////////////
    virtual void on_missing_key_error(string key) {}
    
    /////////////////////////////////////////////////////////////////////////////
    /// Handles a invalid-index error.
    ///
    /// This error-handling method is invoked if any of the reading functions
    /// accepting an `index` parameter fails to access an index in the underlying
    /// JSON array, which means that `index` would overflow the underlying JSON
    /// array's size.
    ///
    /// @param index An invalid index.
    ///
    /////////////////////////////////////////////////////////////////////////////
    virtual void on_index_access_error(int index) {}
    
    /////////////////////////////////////////////////////////////////////////////
    /// Handles an invalid-type error.
    ///
    /// This error-handling method is invoked if any of the reading functions
    /// succeeds in finding a key or accessing an index, but fails to read the
    /// value due its type being different than the expected one.
    ///
    /// @param actual_type The actual type of the read value.
    /// @param expected_type The expected type of the read value.
    ///
    /////////////////////////////////////////////////////////////////////////////
    virtual void on_invalid_key_type_error(string key, JsonType actual_type, JsonType expected_type) {}
    
    virtual void on_invalid_index_type_error(int index, JsonType actual_type, JsonType expected_type) {}

private:
    // Generic functions to read int and cast to `T`.
    template <typename T>
    bool read_int(string key, T& value, bool optional);

    template <typename T>
    bool read_int_at(int index, T& value, bool optional);

    // Generic function to read JSON document values.
    JsonValue* read_value(string key, JsonType expected_type, bool optional);
    
    // Generic function to read JSON array values.
    JsonValue* read_value_at(int index, JsonType expected_type, bool optional);

    const JsonValue* m_root;
};

//===========================================================================
// --- JsonReader implementation ---
//===========================================================================
JsonReader::JsonReader(const JsonValue* value)
{
    reset(value);
}

void JsonReader::reset(const JsonValue* value)
{
    m_root = value;
}

bool JsonReader::read(string key, string& value, bool optional)
{
    JsonValue* elem = read_value(key, JSON_STRING, optional);
    
    if (!elem)
        return false;
    
    value = elem.to_string();
    return true;
}

bool JsonReader::read(string key, double& value, bool optional)
{
    JsonValue* elem = read_value(key, JSON_DOUBLE, optional);
    
    if (!elem)
        return false;
    
    value = elem.to_double();
    return true;
}

bool JsonReader::read(string key, long& value, bool optional)
{
    return read_int(key, value, optional);
}

bool JsonReader::read(string key, int& value, bool optional)
{
    return read_int(key, value, optional);
}

bool JsonReader::read(string key, datetime& value, bool optional)
{
    return read_int(key, value, optional);
}

template <typename T>
bool JsonReader::read_int(string key, T& value, bool optional)
{
    JsonValue* elem = read_value(key, JSON_INTEGER, optional);
    
    if (!elem)
        return false;

    value = T(elem.to_int());
    return true;
}

bool JsonReader::read(string key, bool& value, bool optional)
{
    JsonValue* elem = read_value(key, JSON_BOOL, optional);
    
    if (!elem)
        return false;

    value = elem.to_bool();
    return true;
}

JsonValue* JsonReader::read_value(string key, JsonType expected_type, bool optional)
{
    if (!m_root)
    {
        on_invalid_root_type_error(JSON_UNDEFINED, JSON_OBJECT);
        return NULL;
    }

    if (m_root.type() != JSON_OBJECT)
    {
        on_invalid_root_type_error(m_root.type(), JSON_OBJECT);
        return NULL;
    }

    JsonValue* elem = m_root.find(key);
    
    if (!elem)
    {    
        if (!optional)
            on_missing_key_error(key);
    }
    else if (elem.type() != expected_type)
    {
        if (!optional)
            on_invalid_key_type_error(key, elem.type(), expected_type);
    }

    return elem;
}

bool JsonReader::read_at(int index, string& value, bool optional)
{
    JsonValue* elem = read_value_at(index, JSON_STRING, optional);
    
    if (!elem)
        return false;
    
    value = elem.to_string();
    return true;
}

bool JsonReader::read_at(int index, double& value, bool optional)
{
    JsonValue* elem = read_value_at(index, JSON_DOUBLE, optional);
    
    if (!elem)
        return false;
    
    value = elem.to_double();
    return true;
}

bool JsonReader::read_at(int index, long& value, bool optional)
{
    return read_int_at(index, value, optional);
}

bool JsonReader::read_at(int index, int& value, bool optional)
{
    return read_int_at(index, value, optional);
}

bool JsonReader::read_at(int index, datetime& value, bool optional)
{
    return read_int_at(index, value, optional);
}

template <typename T>
bool JsonReader::read_int_at(int index, T& value, bool optional)
{
    JsonValue* elem = read_value_at(index, JSON_INTEGER, optional);
    
    if (!elem)
        return false;

    value = T(elem.to_int());
    return true;
}

bool JsonReader::read_at(int index, bool& value, bool optional)
{
    JsonValue* elem = read_value_at(index, JSON_BOOL, optional);
    
    if (!elem)
        return false;

    value = elem.to_bool();
    return true;
}

JsonValue* JsonReader::read_value_at(int index, JsonType expected_type, bool optional)
{
    if (!m_root)
    {
        on_invalid_root_type_error(JSON_UNDEFINED, JSON_ARRAY);
        return NULL;
    }

    if (m_root.type() != JSON_ARRAY)
    {
        on_invalid_root_type_error(m_root.type(), JSON_ARRAY);
        return NULL;
    }

    JsonValue* elem = m_root.at(index);

    if (!elem)
    {
        if (!optional)
            on_index_access_error(index);
    }
    else if (elem.type() != expected_type)
    {
        if (!optional)
            on_invalid_index_type_error(index, elem.type(), expected_type);
    }
    
    return elem;
}

template <typename T>
bool JsonReader::read_required(string key, T& value)
{
    return read(key, value, false);
}

template <typename T>
bool JsonReader::read_optional(string key, Optional<T>& opt)
{
    T value;

    if (read(key, value, true))
        opt = value;

    return opt.has_value();
}
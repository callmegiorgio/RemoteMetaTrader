#property strict

// Local
#include "JsonValue.mqh"
#include "JsonReader.mqh"
#include "RequestError.mqh"

/// TODO
class MessageHandler : private JsonReader {
public:
    void process(const JsonValue& request, JsonValue& response);

protected:
    virtual void process() {}
    
    template <typename T>
    bool read_required(string key, T& value)
    {
        return JsonReader::read(key, value, false);
    }
    
    template <typename T>
    bool read_optional(string key, T& value)
    {
        return JsonReader::read(key, value, true);
    }

    template <typename T>
    void write_value(string key, T value)
    {
        m_response[key] = value;
    }
    
    void write_value(string key, const JsonValue& value)
    {
        m_response[key] = value;
    }
    
    void write_result(int result)
    {
        write_value("result", result);
    }
    
    void write_result_last_error()
    {
        write_result(GetLastError());
    }
    
    void write_result_success()
    {
        write_result(ERR_NO_ERROR);
    }
    
    void write_result_invalid_parameter_value(string param)
    {
        write_result(ERR_USER_INVALID_PARAMETER_VALUE);
        write_value("param", param);
    }

private:
    void on_invalid_root_type_error(JsonType actual_type, JsonType expected_type) override
    {
        
    }

    void on_missing_key_error(string key) override
    {
        write_result(ERR_USER_MISSING_REQUIRED_PARAM);
        write_value("param", key);
    }
    
    void on_invalid_key_type_error(string key, JsonType actual_type, JsonType expected_type) override
    {
        write_result(ERR_USER_INVALID_PARAMETER_TYPE);
        write_value("param", key);
    }

    JsonValue* m_response;
};

void MessageHandler::process(const JsonValue& request, JsonValue& response)
{
    JsonReader::reset(GetPointer(request));
    m_response = GetPointer(response);

    process();

    m_response = NULL;
}
#property strict

// Local
#include "../Utility/JsonValue.mqh"
#include "../Utility/JsonReader.mqh"
#include "CommandResult.mqh"

/// TODO
class CommandArguments : public JsonReader {
public:
    CommandArguments(const JsonValue& root);

    CommandResult* result();

private:
    void on_invalid_root_type_error(JsonType actual_type, JsonType expected_type) override;
    void on_missing_key_error(string key) override;
    void on_index_access_error(int index) override;
    void on_invalid_key_type_error(string key, JsonType actual_type, JsonType expected_type) override;
    void on_invalid_index_type_error(int index, JsonType actual_type, JsonType expected_type) override;

    CommandResult m_result;
};

//===========================================================================
// --- CommandArguments implementation ---
//===========================================================================
CommandArguments::CommandArguments(const JsonValue& root)
    : JsonReader(GetPointer(root))
{
    m_result = CommandResult::SUCCESS;
}

CommandResult* CommandArguments::result()
{
    return GetPointer(m_result);
}

void CommandArguments::on_invalid_root_type_error(JsonType actual_type, JsonType expected_type) override
{
    m_result = CommandResult::make_invalid_json(actual_type, expected_type);
}

void CommandArguments::on_missing_key_error(string key) override
{
    m_result = CommandResult::make_missing_key_error(key);
}

void CommandArguments::on_index_access_error(int index) override
{
    m_result = CommandResult::make_missing_index_error(index);
}

void CommandArguments::on_invalid_key_type_error(string key, JsonType actual_type, JsonType expected_type) override
{
    m_result = CommandResult::make_invalid_key_type_error(key, actual_type, expected_type);
}

void CommandArguments::on_invalid_index_type_error(int index, JsonType actual_type, JsonType expected_type) override
{
    m_result = CommandResult::make_invalid_index_type_error(index, actual_type, expected_type);
}
#property strict

// Local
#include "../Utility/JsonValue.mqh"

////////////////////////////////////////////////////////////////////////////////
/// Stores the result of a command execution.
///
/// The class `CommandResult` stores the result of a command execution made by
/// `CommandDispatcher::execute()`. A result contains two properties, a code
/// and a message.
///
/// A command result code is a superset of the set of stardard MQL error codes
/// and the set of codes defined by the RMT library. Codes defined by this class
/// are enclosed within its scope as `static const` identifiers. Identifiers 
/// representing MQL error codes have the same value and a similar name to MQL
/// ones, with the exception of `ERR_NO_ERROR` and `ERR_NO_MQLERROR`, which are
/// combined into one identifier named `CommandResult::SUCCESS`.
///
/// An object of this class also stores an optional JSON message that may be
/// returned along with a code to give further information about an error, or
/// to send results of a processed request.
///
/// This class implements static methods to create objects for RMT-defined error
/// codes, and as such works as a kind of protocol. Error description messages
/// have mainly an optional nature, since once an error occurs, shit will have
/// already happened, so anything else that comes with the message will be a
/// bonus. This is why MQL-native data types, such as those for requests and
/// responses, are defined for error messages, which are instead described by
/// the static methods of this class.
///
////////////////////////////////////////////////////////////////////////////////
class CommandResult {
public:
    static const int SUCCESS;
    static const int INVALID_REQUEST;         /// Request message does not match the protocol's format.
    static const int UNKNOWN_REQUEST_COMMAND; /// Request message syntax is correct, but command is not registered by the server.
    static const int INVALID_JSON;            /// Command is registered and content is provided, but content is not a valid JSON document.
    static const int MISSING_JSON_KEY;        /// Content is valid JSON, but a required key is missing.
    static const int MISSING_JSON_INDEX;      /// Content is valid JSON, but a required index is missing.
    static const int INVALID_JSON_KEY_TYPE;   /// A required key is found, but its value type differs from the expected type.
    static const int INVALID_JSON_INDEX_TYPE; /// A required index is found, but its value type differs from the expected type.
    static const int INVALID_ORDER_STATUS;    /// The current order status does not allow this kind of operation.
    static const int EXCHANGE_RATE_FAILED;
    static const int NO_RESULT;
    static const int COMMON_ERROR;
    static const int INVALID_TRADE_PARAMETERS;
    static const int SERVER_BUSY;
    static const int OLD_VERSION;
    static const int NO_CONNECTION;
    static const int NOT_ENOUGH_RIGHTS;
    static const int TOO_FREQUENT_REQUESTS;
    static const int MALFUNCTIONAL_TRADE;
    static const int ACCOUNT_DISABLED;
    static const int INVALID_ACCOUNT;
    static const int TRADE_TIMEOUT;
    static const int INVALID_PRICE;
    static const int INVALID_STOPS;
    static const int INVALID_TRADE_VOLUME;
    static const int MARKET_CLOSED;
    static const int TRADE_DISABLED;
    static const int NOT_ENOUGH_MONEY;
    static const int PRICE_CHANGED;
    static const int OFF_QUOTES;
    static const int BROKER_BUSY;
    static const int REQUOTE;
    static const int ORDER_LOCKED;
    static const int LONG_POSITIONS_ONLY_ALLOWED;
    static const int TOO_MANY_REQUESTS;
    static const int TRADE_MODIFY_DENIED;
    static const int TRADE_CONTEXT_BUSY;
    static const int TRADE_EXPIRATION_DENIED;
    static const int TRADE_TOO_MANY_ORDERS;
    static const int TRADE_HEDGE_PROHIBITED;
    static const int TRADE_PROHIBITED_BY_FIFO;
    static const int WRONG_FUNCTION_POINTER;
    static const int ARRAY_INDEX_OUT_OF_RANGE;
    static const int NO_MEMORY_FOR_CALL_STACK;
    static const int RECURSIVE_STACK_OVERFLOW;
    static const int NOT_ENOUGH_STACK_FOR_PARAM;
    static const int NO_MEMORY_FOR_PARAM_STRING;
    static const int NO_MEMORY_FOR_TEMP_STRING;
    static const int NOT_INITIALIZED_STRING;
    static const int NOT_INITIALIZED_ARRAYSTRING;
    static const int NO_MEMORY_FOR_ARRAYSTRING;
    static const int TOO_LONG_STRING;
    static const int REMAINDER_FROM_ZERO_DIVIDE;
    static const int ZERO_DIVIDE;
    static const int UNKNOWN_COMMAND;
    static const int WRONG_JUMP;
    static const int NOT_INITIALIZED_ARRAY;
    static const int DLL_CALLS_NOT_ALLOWED;
    static const int CANNOT_LOAD_LIBRARY;
    static const int CANNOT_CALL_FUNCTION;
    static const int EXTERNAL_CALLS_NOT_ALLOWED;
    static const int NO_MEMORY_FOR_RETURNED_STR;
    static const int SYSTEM_BUSY;
    static const int DLLFUNC_CRITICALERROR;
    static const int INTERNAL_ERROR;
    static const int OUT_OF_MEMORY;
    static const int INVALID_POINTER;
    static const int FORMAT_TOO_MANY_FORMATTERS;
    static const int FORMAT_TOO_MANY_PARAMETERS;
    static const int ARRAY_INVALID;
    static const int CHART_NOREPLY;
    static const int INVALID_FUNCTION_PARAMSCNT;
    static const int INVALID_FUNCTION_PARAMVALUE;
    static const int STRING_FUNCTION_INTERNAL;
    static const int SOME_ARRAY_ERROR;
    static const int INCORRECT_SERIESARRAY_USING;
    static const int CUSTOM_INDICATOR_ERROR;
    static const int INCOMPATIBLE_ARRAYS;
    static const int GLOBAL_VARIABLES_PROCESSING;
    static const int GLOBAL_VARIABLE_NOT_FOUND;
    static const int FUNC_NOT_ALLOWED_IN_TESTING;
    static const int FUNCTION_NOT_CONFIRMED;
    static const int SEND_MAIL_ERROR;
    static const int STRING_PARAMETER_EXPECTED;
    static const int INTEGER_PARAMETER_EXPECTED;
    static const int DOUBLE_PARAMETER_EXPECTED;
    static const int ARRAY_AS_PARAMETER_EXPECTED;
    static const int HISTORY_WILL_UPDATED;
    static const int TRADE_ERROR;
    static const int RESOURCE_NOT_FOUND;
    static const int RESOURCE_NOT_SUPPORTED;
    static const int RESOURCE_DUPLICATED;
    static const int INDICATOR_CANNOT_INIT;
    static const int INDICATOR_CANNOT_LOAD;
    static const int NO_HISTORY_DATA;
    static const int NO_MEMORY_FOR_HISTORY;
    static const int NO_MEMORY_FOR_INDICATOR;
    static const int END_OF_FILE;
    static const int SOME_FILE_ERROR;
    static const int WRONG_FILE_NAME;
    static const int TOO_MANY_OPENED_FILES;
    static const int CANNOT_OPEN_FILE;
    static const int INCOMPATIBLE_FILEACCESS;
    static const int NO_ORDER_SELECTED;
    static const int UNKNOWN_SYMBOL;
    static const int INVALID_PRICE_PARAM;
    static const int INVALID_TICKET;
    static const int TRADE_NOT_ALLOWED;
    static const int LONGS_NOT_ALLOWED;
    static const int SHORTS_NOT_ALLOWED;
    static const int OBJECT_ALREADY_EXISTS;
    static const int UNKNOWN_OBJECT_PROPERTY;
    static const int OBJECT_DOES_NOT_EXIST;
    static const int UNKNOWN_OBJECT_TYPE;
    static const int NO_OBJECT_NAME;
    static const int OBJECT_COORDINATES_ERROR;
    static const int NO_SPECIFIED_SUBWINDOW;
    static const int SOME_OBJECT_ERROR;
    static const int CHART_PROP_INVALID;
    static const int CHART_NOT_FOUND;
    static const int CHARTWINDOW_NOT_FOUND;
    static const int CHARTINDICATOR_NOT_FOUND;
    static const int SYMBOL_SELECT;
    static const int NOTIFICATION_ERROR;
    static const int NOTIFICATION_PARAMETER;
    static const int NOTIFICATION_SETTINGS;
    static const int NOTIFICATION_TOO_FREQUENT;
    static const int FTP_NOSERVER;
    static const int FTP_NOLOGIN;
    static const int FTP_CONNECT_FAILED;
    static const int FTP_CLOSED;
    static const int FTP_CHANGEDIR;
    static const int FTP_FILE_ERROR;
    static const int FTP_ERROR;
    static const int FILE_TOO_MANY_OPENED;
    static const int FILE_WRONG_FILENAME;
    static const int FILE_TOO_LONG_FILENAME;
    static const int FILE_CANNOT_OPEN;
    static const int FILE_BUFFER_ALLOCATION_ERROR;
    static const int FILE_CANNOT_DELETE;
    static const int FILE_INVALID_HANDLE;
    static const int FILE_WRONG_HANDLE;
    static const int FILE_NOT_TOWRITE;
    static const int FILE_NOT_TOREAD;
    static const int FILE_NOT_BIN;
    static const int FILE_NOT_TXT;
    static const int FILE_NOT_TXTORCSV;
    static const int FILE_NOT_CSV;
    static const int FILE_READ_ERROR;
    static const int FILE_WRITE_ERROR;
    static const int FILE_BIN_STRINGSIZE;
    static const int FILE_INCOMPATIBLE;
    static const int FILE_IS_DIRECTORY;
    static const int FILE_NOT_EXIST;
    static const int FILE_CANNOT_REWRITE;
    static const int FILE_WRONG_DIRECTORYNAME;
    static const int FILE_DIRECTORY_NOT_EXIST;
    static const int FILE_NOT_DIRECTORY;
    static const int FILE_CANNOT_DELETE_DIRECTORY;
    static const int FILE_CANNOT_CLEAN_DIRECTORY;
    static const int FILE_ARRAYRESIZE_ERROR;
    static const int FILE_STRINGRESIZE_ERROR;
    static const int FILE_STRUCT_WITH_OBJECTS;

    ////////////////////////////////////////////////////////////////////////////////
    /// Returns a `CommandResult` object with code `CommandResult::INVALID_JSON` and
    /// the following JSON message:
    ///
    /// {
    ///   "actual": string,
    ///   "expected": string
    /// }
    ///
    ////////////////////////////////////////////////////////////////////////////////
    static CommandResult make_invalid_json(JsonType actual_type, JsonType expected_type);

    ////////////////////////////////////////////////////////////////////////////////
    /// Returns a `CommandResult` object with code `CommandResult::MISSING_JSON_KEY`
    /// and the following JSON message:
    ///
    /// {
    ///   "key": string
    /// }
    ///
    ////////////////////////////////////////////////////////////////////////////////
    static CommandResult make_missing_key_error(string key);

    ////////////////////////////////////////////////////////////////////////////////
    /// Returns a `CommandResult` object with code `CommandResult::MISSING_JSON_INDEX`
    /// and the following JSON message:
    ///
    /// {
    ///   "index": int
    /// }
    ///
    ////////////////////////////////////////////////////////////////////////////////
    static CommandResult make_missing_index_error(int index);

    ////////////////////////////////////////////////////////////////////////////////
    /// Returns a `CommandResult` object with code `CommandResult::INVALID_JSON_KEY_TYPE`
    /// and the following JSON message:
    ///
    /// {
    ///   "key": string,
    ///   "actual": string,
    ///   "expected": string
    /// }
    ///
    ////////////////////////////////////////////////////////////////////////////////
    static CommandResult make_invalid_key_type_error(string key, JsonType actual_type, JsonType expected_type);

    ////////////////////////////////////////////////////////////////////////////////
    /// Returns a `CommandResult` object with code `CommandResult::INVALID_JSON_INDEX_TYPE`
    /// and the following JSON message:
    ///
    /// {
    ///   "index": int,
    ///   "actual": string,
    ///   "expected": string
    /// }
    ///
    ////////////////////////////////////////////////////////////////////////////////
    static CommandResult make_invalid_index_type_error(int index, JsonType actual_type, JsonType expected_type);

    ////////////////////////////////////////////////////////////////////////////////
    /// Returns a `CommandResult` object with code `CommandResult::INVALID_ORDER_STATUS`
    /// and the following JSON message:
    ///
    /// {
    ///   "actual": string,
    ///   "expected": string
    /// }
    ///
    ////////////////////////////////////////////////////////////////////////////////
    static CommandResult make_invalid_order_status(string actual_status, string expected_status);

    CommandResult();

    CommandResult(int code);

    CommandResult(const CommandResult& other);

    int code() const;

    JsonValue* message();

    JsonValue* message(string key);

    void operator=(int code);

private:
    void set_code(int code);

    int       m_code;
    JsonValue m_message;
};

//===========================================================================
// --- CommandResult implementation ---
//===========================================================================
static const int CommandResult::SUCCESS                      = 0;
static const int CommandResult::INVALID_REQUEST              = -10000;
static const int CommandResult::UNKNOWN_REQUEST_COMMAND      = -10001;
static const int CommandResult::INVALID_JSON                 = -10002;
static const int CommandResult::MISSING_JSON_KEY             = -10003;
static const int CommandResult::MISSING_JSON_INDEX           = -10004;
static const int CommandResult::INVALID_JSON_KEY_TYPE        = -10005;
static const int CommandResult::INVALID_JSON_INDEX_TYPE      = -10006;
static const int CommandResult::INVALID_ORDER_STATUS         = -10007;
static const int CommandResult::EXCHANGE_RATE_FAILED         = -10008;
static const int CommandResult::NO_RESULT                    = 1;
static const int CommandResult::COMMON_ERROR                 = 2;
static const int CommandResult::INVALID_TRADE_PARAMETERS     = 3;
static const int CommandResult::SERVER_BUSY                  = 4;
static const int CommandResult::OLD_VERSION                  = 5;
static const int CommandResult::NO_CONNECTION                = 6;
static const int CommandResult::NOT_ENOUGH_RIGHTS            = 7;
static const int CommandResult::TOO_FREQUENT_REQUESTS        = 8;
static const int CommandResult::MALFUNCTIONAL_TRADE          = 9;
static const int CommandResult::ACCOUNT_DISABLED             = 64;
static const int CommandResult::INVALID_ACCOUNT              = 65;
static const int CommandResult::TRADE_TIMEOUT                = 128;
static const int CommandResult::INVALID_PRICE                = 129;
static const int CommandResult::INVALID_STOPS                = 130;
static const int CommandResult::INVALID_TRADE_VOLUME         = 131;
static const int CommandResult::MARKET_CLOSED                = 132;
static const int CommandResult::TRADE_DISABLED               = 133;
static const int CommandResult::NOT_ENOUGH_MONEY             = 134;
static const int CommandResult::PRICE_CHANGED                = 135;
static const int CommandResult::OFF_QUOTES                   = 136;
static const int CommandResult::BROKER_BUSY                  = 137;
static const int CommandResult::REQUOTE                      = 138;
static const int CommandResult::ORDER_LOCKED                 = 139;
static const int CommandResult::LONG_POSITIONS_ONLY_ALLOWED  = 140;
static const int CommandResult::TOO_MANY_REQUESTS            = 141;
static const int CommandResult::TRADE_MODIFY_DENIED          = 145;
static const int CommandResult::TRADE_CONTEXT_BUSY           = 146;
static const int CommandResult::TRADE_EXPIRATION_DENIED      = 147;
static const int CommandResult::TRADE_TOO_MANY_ORDERS        = 148;
static const int CommandResult::TRADE_HEDGE_PROHIBITED       = 149;
static const int CommandResult::TRADE_PROHIBITED_BY_FIFO     = 150;
static const int CommandResult::WRONG_FUNCTION_POINTER       = 4001;
static const int CommandResult::ARRAY_INDEX_OUT_OF_RANGE     = 4002;
static const int CommandResult::NO_MEMORY_FOR_CALL_STACK     = 4003;
static const int CommandResult::RECURSIVE_STACK_OVERFLOW     = 4004;
static const int CommandResult::NOT_ENOUGH_STACK_FOR_PARAM   = 4005;
static const int CommandResult::NO_MEMORY_FOR_PARAM_STRING   = 4006;
static const int CommandResult::NO_MEMORY_FOR_TEMP_STRING    = 4007;
static const int CommandResult::NOT_INITIALIZED_STRING       = 4008;
static const int CommandResult::NOT_INITIALIZED_ARRAYSTRING  = 4009;
static const int CommandResult::NO_MEMORY_FOR_ARRAYSTRING    = 4010;
static const int CommandResult::TOO_LONG_STRING              = 4011;
static const int CommandResult::REMAINDER_FROM_ZERO_DIVIDE   = 4012;
static const int CommandResult::ZERO_DIVIDE                  = 4013;
static const int CommandResult::UNKNOWN_COMMAND              = 4014;
static const int CommandResult::WRONG_JUMP                   = 4015;
static const int CommandResult::NOT_INITIALIZED_ARRAY        = 4016;
static const int CommandResult::DLL_CALLS_NOT_ALLOWED        = 4017;
static const int CommandResult::CANNOT_LOAD_LIBRARY          = 4018;
static const int CommandResult::CANNOT_CALL_FUNCTION         = 4019;
static const int CommandResult::EXTERNAL_CALLS_NOT_ALLOWED   = 4020;
static const int CommandResult::NO_MEMORY_FOR_RETURNED_STR   = 4021;
static const int CommandResult::SYSTEM_BUSY                  = 4022;
static const int CommandResult::DLLFUNC_CRITICALERROR        = 4023;
static const int CommandResult::INTERNAL_ERROR               = 4024;
static const int CommandResult::OUT_OF_MEMORY                = 4025;
static const int CommandResult::INVALID_POINTER              = 4026;
static const int CommandResult::FORMAT_TOO_MANY_FORMATTERS   = 4027;
static const int CommandResult::FORMAT_TOO_MANY_PARAMETERS   = 4028;
static const int CommandResult::ARRAY_INVALID                = 4029;
static const int CommandResult::CHART_NOREPLY                = 4030;
static const int CommandResult::INVALID_FUNCTION_PARAMSCNT   = 4050;
static const int CommandResult::INVALID_FUNCTION_PARAMVALUE  = 4051;
static const int CommandResult::STRING_FUNCTION_INTERNAL     = 4052;
static const int CommandResult::SOME_ARRAY_ERROR             = 4053;
static const int CommandResult::INCORRECT_SERIESARRAY_USING  = 4054;
static const int CommandResult::CUSTOM_INDICATOR_ERROR       = 4055;
static const int CommandResult::INCOMPATIBLE_ARRAYS          = 4056;
static const int CommandResult::GLOBAL_VARIABLES_PROCESSING  = 4057;
static const int CommandResult::GLOBAL_VARIABLE_NOT_FOUND    = 4058;
static const int CommandResult::FUNC_NOT_ALLOWED_IN_TESTING  = 4059;
static const int CommandResult::FUNCTION_NOT_CONFIRMED       = 4060;
static const int CommandResult::SEND_MAIL_ERROR              = 4061;
static const int CommandResult::STRING_PARAMETER_EXPECTED    = 4062;
static const int CommandResult::INTEGER_PARAMETER_EXPECTED   = 4063;
static const int CommandResult::DOUBLE_PARAMETER_EXPECTED    = 4064;
static const int CommandResult::ARRAY_AS_PARAMETER_EXPECTED  = 4065;
static const int CommandResult::HISTORY_WILL_UPDATED         = 4066;
static const int CommandResult::TRADE_ERROR                  = 4067;
static const int CommandResult::RESOURCE_NOT_FOUND           = 4068;
static const int CommandResult::RESOURCE_NOT_SUPPORTED       = 4069;
static const int CommandResult::RESOURCE_DUPLICATED          = 4070;
static const int CommandResult::INDICATOR_CANNOT_INIT        = 4071;
static const int CommandResult::INDICATOR_CANNOT_LOAD        = 4072;
static const int CommandResult::NO_HISTORY_DATA              = 4073;
static const int CommandResult::NO_MEMORY_FOR_HISTORY        = 4074;
static const int CommandResult::NO_MEMORY_FOR_INDICATOR      = 4075;
static const int CommandResult::END_OF_FILE                  = 4099;
static const int CommandResult::SOME_FILE_ERROR              = 4100;
static const int CommandResult::WRONG_FILE_NAME              = 4101;
static const int CommandResult::TOO_MANY_OPENED_FILES        = 4102;
static const int CommandResult::CANNOT_OPEN_FILE             = 4103;
static const int CommandResult::INCOMPATIBLE_FILEACCESS      = 4104;
static const int CommandResult::NO_ORDER_SELECTED            = 4105;
static const int CommandResult::UNKNOWN_SYMBOL               = 4106;
static const int CommandResult::INVALID_PRICE_PARAM          = 4107;
static const int CommandResult::INVALID_TICKET               = 4108;
static const int CommandResult::TRADE_NOT_ALLOWED            = 4109;
static const int CommandResult::LONGS_NOT_ALLOWED            = 4110;
static const int CommandResult::SHORTS_NOT_ALLOWED           = 4111;
static const int CommandResult::OBJECT_ALREADY_EXISTS        = 4200;
static const int CommandResult::UNKNOWN_OBJECT_PROPERTY      = 4201;
static const int CommandResult::OBJECT_DOES_NOT_EXIST        = 4202;
static const int CommandResult::UNKNOWN_OBJECT_TYPE          = 4203;
static const int CommandResult::NO_OBJECT_NAME               = 4204;
static const int CommandResult::OBJECT_COORDINATES_ERROR     = 4205;
static const int CommandResult::NO_SPECIFIED_SUBWINDOW       = 4206;
static const int CommandResult::SOME_OBJECT_ERROR            = 4207;
static const int CommandResult::CHART_PROP_INVALID           = 4210;
static const int CommandResult::CHART_NOT_FOUND              = 4211;
static const int CommandResult::CHARTWINDOW_NOT_FOUND        = 4212;
static const int CommandResult::CHARTINDICATOR_NOT_FOUND     = 4213;
static const int CommandResult::SYMBOL_SELECT                = 4220;
static const int CommandResult::NOTIFICATION_ERROR           = 4250;
static const int CommandResult::NOTIFICATION_PARAMETER       = 4251;
static const int CommandResult::NOTIFICATION_SETTINGS        = 4252;
static const int CommandResult::NOTIFICATION_TOO_FREQUENT    = 4253;
static const int CommandResult::FTP_NOSERVER                 = 4260;
static const int CommandResult::FTP_NOLOGIN                  = 4261;
static const int CommandResult::FTP_CONNECT_FAILED           = 4262;
static const int CommandResult::FTP_CLOSED                   = 4263;
static const int CommandResult::FTP_CHANGEDIR                = 4264;
static const int CommandResult::FTP_FILE_ERROR               = 4265;
static const int CommandResult::FTP_ERROR                    = 4266;
static const int CommandResult::FILE_TOO_MANY_OPENED         = 5001;
static const int CommandResult::FILE_WRONG_FILENAME          = 5002;
static const int CommandResult::FILE_TOO_LONG_FILENAME       = 5003;
static const int CommandResult::FILE_CANNOT_OPEN             = 5004;
static const int CommandResult::FILE_BUFFER_ALLOCATION_ERROR = 5005;
static const int CommandResult::FILE_CANNOT_DELETE           = 5006;
static const int CommandResult::FILE_INVALID_HANDLE          = 5007;
static const int CommandResult::FILE_WRONG_HANDLE            = 5008;
static const int CommandResult::FILE_NOT_TOWRITE             = 5009;
static const int CommandResult::FILE_NOT_TOREAD              = 5010;
static const int CommandResult::FILE_NOT_BIN                 = 5011;
static const int CommandResult::FILE_NOT_TXT                 = 5012;
static const int CommandResult::FILE_NOT_TXTORCSV            = 5013;
static const int CommandResult::FILE_NOT_CSV                 = 5014;
static const int CommandResult::FILE_READ_ERROR              = 5015;
static const int CommandResult::FILE_WRITE_ERROR             = 5016;
static const int CommandResult::FILE_BIN_STRINGSIZE          = 5017;
static const int CommandResult::FILE_INCOMPATIBLE            = 5018;
static const int CommandResult::FILE_IS_DIRECTORY            = 5019;
static const int CommandResult::FILE_NOT_EXIST               = 5020;
static const int CommandResult::FILE_CANNOT_REWRITE          = 5021;
static const int CommandResult::FILE_WRONG_DIRECTORYNAME     = 5022;
static const int CommandResult::FILE_DIRECTORY_NOT_EXIST     = 5023;
static const int CommandResult::FILE_NOT_DIRECTORY           = 5024;
static const int CommandResult::FILE_CANNOT_DELETE_DIRECTORY = 5025;
static const int CommandResult::FILE_CANNOT_CLEAN_DIRECTORY  = 5026;
static const int CommandResult::FILE_ARRAYRESIZE_ERROR       = 5027;
static const int CommandResult::FILE_STRINGRESIZE_ERROR      = 5028;
static const int CommandResult::FILE_STRUCT_WITH_OBJECTS     = 5029;

static CommandResult CommandResult::make_invalid_json(JsonType actual_type, JsonType expected_type)
{
    CommandResult cmd_result = CommandResult::INVALID_JSON;

    cmd_result.message("actual")   = json_type_to_string(actual_type);
    cmd_result.message("expected") = json_type_to_string(expected_type);

    return cmd_result;
}

static CommandResult CommandResult::make_missing_key_error(string key)
{
    CommandResult cmd_result = CommandResult::MISSING_JSON_KEY;

    cmd_result.message("key") = key;

    return cmd_result;
}

static CommandResult CommandResult::make_missing_index_error(int index)
{
    CommandResult cmd_result = CommandResult::MISSING_JSON_INDEX;
    
    cmd_result.message("index") = index;

    return cmd_result;
}

static CommandResult CommandResult::make_invalid_key_type_error(string key, JsonType actual_type, JsonType expected_type)
{
    CommandResult cmd_result = CommandResult::INVALID_JSON_KEY_TYPE;

    cmd_result.message("key")      = key;
    cmd_result.message("actual")   = json_type_to_string(actual_type);
    cmd_result.message("expected") = json_type_to_string(expected_type);

    return cmd_result;
}

static CommandResult CommandResult::make_invalid_index_type_error(int index, JsonType actual_type, JsonType expected_type)
{
    CommandResult cmd_result = CommandResult::INVALID_JSON_INDEX_TYPE;

    cmd_result.message("index")    = index;
    cmd_result.message("actual")   = json_type_to_string(actual_type);
    cmd_result.message("expected") = json_type_to_string(expected_type);

    return cmd_result;
}

static CommandResult CommandResult::make_invalid_order_status(string actual_status, string expected_status)
{
    CommandResult cmd_result = CommandResult::INVALID_ORDER_STATUS;
            
    cmd_result.message("actual")   = actual_status;
    cmd_result.message("expected") = expected_status;

    return cmd_result;
}

CommandResult::CommandResult()
{
    m_code = CommandResult::SUCCESS;
}

CommandResult::CommandResult(int code)
{
    set_code(code);
}

CommandResult::CommandResult(const CommandResult& other)
{
    m_code   = other.m_code;
    m_message = other.m_message;
}

void CommandResult::set_code(int code)
{
    if (code == ERR_NO_MQLERROR)
        m_code = CommandResult::SUCCESS;
    else
        m_code = code;
}

JsonValue* CommandResult::message()
{
    return GetPointer(m_message);
}

JsonValue* CommandResult::message(string key)
{
    return m_message[key];
}

int CommandResult::code() const
{
    return m_code;
}

void CommandResult::operator=(int code)
{
    set_code(code);
}
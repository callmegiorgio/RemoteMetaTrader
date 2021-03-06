from enum import IntEnum

class CommandResultCode(IntEnum):
    SUCCESS                      = 0
    INVALID_REQUEST              = -10000
    UNKNOWN_REQUEST_COMMAND      = -10001
    INVALID_JSON                 = -10002
    MISSING_JSON_KEY             = -10003
    MISSING_JSON_INDEX           = -10004
    INVALID_JSON_KEY_TYPE        = -10005
    INVALID_JSON_INDEX_TYPE      = -10006
    INVALID_ORDER_STATUS         = -10007
    NO_RESULT                    = 1
    COMMON_ERROR                 = 2
    INVALID_TRADE_PARAMETERS     = 3
    SERVER_BUSY                  = 4
    OLD_VERSION                  = 5
    NO_CONNECTION                = 6
    NOT_ENOUGH_RIGHTS            = 7
    TOO_FREQUENT_REQUESTS        = 8
    MALFUNCTIONAL_TRADE          = 9
    ACCOUNT_DISABLED             = 64
    INVALID_ACCOUNT              = 65
    TRADE_TIMEOUT                = 128
    INVALID_PRICE                = 129
    INVALID_STOPS                = 130
    INVALID_TRADE_VOLUME         = 131
    MARKET_CLOSED                = 132
    TRADE_DISABLED               = 133
    NOT_ENOUGH_MONEY             = 134
    PRICE_CHANGED                = 135
    OFF_QUOTES                   = 136
    BROKER_BUSY                  = 137
    REQUOTE                      = 138
    ORDER_LOCKED                 = 139
    LONG_POSITIONS_ONLY_ALLOWED  = 140
    TOO_MANY_REQUESTS            = 141
    TRADE_MODIFY_DENIED          = 145
    TRADE_CONTEXT_BUSY           = 146
    TRADE_EXPIRATION_DENIED      = 147
    TRADE_TOO_MANY_ORDERS        = 148
    TRADE_HEDGE_PROHIBITED       = 149
    TRADE_PROHIBITED_BY_FIFO     = 150
    WRONG_FUNCTION_POINTER       = 4001
    ARRAY_INDEX_OUT_OF_RANGE     = 4002
    NO_MEMORY_FOR_CALL_STACK     = 4003
    RECURSIVE_STACK_OVERFLOW     = 4004
    NOT_ENOUGH_STACK_FOR_PARAM   = 4005
    NO_MEMORY_FOR_PARAM_STRING   = 4006
    NO_MEMORY_FOR_TEMP_STRING    = 4007
    NOT_INITIALIZED_STRING       = 4008
    NOT_INITIALIZED_ARRAYSTRING  = 4009
    NO_MEMORY_FOR_ARRAYSTRING    = 4010
    TOO_LONG_STRING              = 4011
    REMAINDER_FROM_ZERO_DIVIDE   = 4012
    ZERO_DIVIDE                  = 4013
    UNKNOWN_COMMAND              = 4014
    WRONG_JUMP                   = 4015
    NOT_INITIALIZED_ARRAY        = 4016
    DLL_CALLS_NOT_ALLOWED        = 4017
    CANNOT_LOAD_LIBRARY          = 4018
    CANNOT_CALL_FUNCTION         = 4019
    EXTERNAL_CALLS_NOT_ALLOWED   = 4020
    NO_MEMORY_FOR_RETURNED_STR   = 4021
    SYSTEM_BUSY                  = 4022
    DLLFUNC_CRITICALERROR        = 4023
    INTERNAL_ERROR               = 4024
    OUT_OF_MEMORY                = 4025
    INVALID_POINTER              = 4026
    FORMAT_TOO_MANY_FORMATTERS   = 4027
    FORMAT_TOO_MANY_PARAMETERS   = 4028
    ARRAY_INVALID                = 4029
    CHART_NOREPLY                = 4030
    INVALID_FUNCTION_PARAMSCNT   = 4050
    INVALID_FUNCTION_PARAMVALUE  = 4051
    STRING_FUNCTION_INTERNAL     = 4052
    SOME_ARRAY_ERROR             = 4053
    INCORRECT_SERIESARRAY_USING  = 4054
    CUSTOM_INDICATOR_ERROR       = 4055
    INCOMPATIBLE_ARRAYS          = 4056
    GLOBAL_VARIABLES_PROCESSING  = 4057
    GLOBAL_VARIABLE_NOT_FOUND    = 4058
    FUNC_NOT_ALLOWED_IN_TESTING  = 4059
    FUNCTION_NOT_CONFIRMED       = 4060
    SEND_MAIL_ERROR              = 4061
    STRING_PARAMETER_EXPECTED    = 4062
    INTEGER_PARAMETER_EXPECTED   = 4063
    DOUBLE_PARAMETER_EXPECTED    = 4064
    ARRAY_AS_PARAMETER_EXPECTED  = 4065
    HISTORY_WILL_UPDATED         = 4066
    TRADE_ERROR                  = 4067
    RESOURCE_NOT_FOUND           = 4068
    RESOURCE_NOT_SUPPORTED       = 4069
    RESOURCE_DUPLICATED          = 4070
    INDICATOR_CANNOT_INIT        = 4071
    INDICATOR_CANNOT_LOAD        = 4072
    NO_HISTORY_DATA              = 4073
    NO_MEMORY_FOR_HISTORY        = 4074
    NO_MEMORY_FOR_INDICATOR      = 4075
    END_OF_FILE                  = 4099
    SOME_FILE_ERROR              = 4100
    WRONG_FILE_NAME              = 4101
    TOO_MANY_OPENED_FILES        = 4102
    CANNOT_OPEN_FILE             = 4103
    INCOMPATIBLE_FILEACCESS      = 4104
    NO_ORDER_SELECTED            = 4105
    UNKNOWN_SYMBOL               = 4106
    INVALID_PRICE_PARAM          = 4107
    INVALID_TICKET               = 4108
    TRADE_NOT_ALLOWED            = 4109
    LONGS_NOT_ALLOWED            = 4110
    SHORTS_NOT_ALLOWED           = 4111
    OBJECT_ALREADY_EXISTS        = 4200
    UNKNOWN_OBJECT_PROPERTY      = 4201
    OBJECT_DOES_NOT_EXIST        = 4202
    UNKNOWN_OBJECT_TYPE          = 4203
    NO_OBJECT_NAME               = 4204
    OBJECT_COORDINATES_ERROR     = 4205
    NO_SPECIFIED_SUBWINDOW       = 4206
    SOME_OBJECT_ERROR            = 4207
    CHART_PROP_INVALID           = 4210
    CHART_NOT_FOUND              = 4211
    CHARTWINDOW_NOT_FOUND        = 4212
    CHARTINDICATOR_NOT_FOUND     = 4213
    SYMBOL_SELECT                = 4220
    NOTIFICATION_ERROR           = 4250
    NOTIFICATION_PARAMETER       = 4251
    NOTIFICATION_SETTINGS        = 4252
    NOTIFICATION_TOO_FREQUENT    = 4253
    FTP_NOSERVER                 = 4260
    FTP_NOLOGIN                  = 4261
    FTP_CONNECT_FAILED           = 4262
    FTP_CLOSED                   = 4263
    FTP_CHANGEDIR                = 4264
    FTP_FILE_ERROR               = 4265
    FTP_ERROR                    = 4266
    FILE_TOO_MANY_OPENED         = 5001
    FILE_WRONG_FILENAME          = 5002
    FILE_TOO_LONG_FILENAME       = 5003
    FILE_CANNOT_OPEN             = 5004
    FILE_BUFFER_ALLOCATION_ERROR = 5005
    FILE_CANNOT_DELETE           = 5006
    FILE_INVALID_HANDLE          = 5007
    FILE_WRONG_HANDLE            = 5008
    FILE_NOT_TOWRITE             = 5009
    FILE_NOT_TOREAD              = 5010
    FILE_NOT_BIN                 = 5011
    FILE_NOT_TXT                 = 5012
    FILE_NOT_TXTORCSV            = 5013
    FILE_NOT_CSV                 = 5014
    FILE_READ_ERROR              = 5015
    FILE_WRITE_ERROR             = 5016
    FILE_BIN_STRINGSIZE          = 5017
    FILE_INCOMPATIBLE            = 5018
    FILE_IS_DIRECTORY            = 5019
    FILE_NOT_EXIST               = 5020
    FILE_CANNOT_REWRITE          = 5021
    FILE_WRONG_DIRECTORYNAME     = 5022
    FILE_DIRECTORY_NOT_EXIST     = 5023
    FILE_NOT_DIRECTORY           = 5024
    FILE_CANNOT_DELETE_DIRECTORY = 5025
    FILE_CANNOT_CLEAN_DIRECTORY  = 5026
    FILE_ARRAYRESIZE_ERROR       = 5027
    FILE_STRINGRESIZE_ERROR      = 5028
    FILE_STRUCT_WITH_OBJECTS     = 5029
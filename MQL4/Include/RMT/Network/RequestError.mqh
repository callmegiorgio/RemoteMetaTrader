#property strict

/// Enumeration of values representing a request error.
enum RequestError {
    ERR_USER_UNRECOGNIZED_COMMAND    = -1,
    ERR_USER_MISSING_REQUIRED_PARAM  = -2,
    ERR_USER_INVALID_PARAMETER_TYPE  = -3,
    ERR_USER_INVALID_PARAMETER_VALUE = -4
};
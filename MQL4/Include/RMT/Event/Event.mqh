#property strict

// Local
#include "../Utility/JsonValue.mqh"

interface Event {
    string name() const;
    JsonValue content() const;
};
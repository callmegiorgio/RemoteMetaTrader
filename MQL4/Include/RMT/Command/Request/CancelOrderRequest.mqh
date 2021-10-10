#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// Request:
/// {
///   "ticket": integer
/// }
class CancelOrderRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        return reader.read_required("ticket", this.ticket);
    }

    int ticket;
};
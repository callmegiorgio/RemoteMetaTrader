#property strict

// Local
#include "../../Utility/JsonReader.mqh"

/// Request:
/// {
///   "ticket":   integer
/// }
class GetOrderRequest {
public:
    bool deserialize(JsonReader& reader)
    {
        return reader.read_required("ticket", this.ticket);
    }

    int ticket;
};
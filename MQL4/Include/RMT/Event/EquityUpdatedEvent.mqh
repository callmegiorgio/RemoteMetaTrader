#property strict

// Local
#include "../Utility/Optional.mqh"

/// Event notified when the account's equity and associated information is updated.
class EquityUpdatedEvent {
public:
    double equity;
    double profit;
    double margin;
    double margin_level;
    double free_margin;

    Optional<double> balance;
};
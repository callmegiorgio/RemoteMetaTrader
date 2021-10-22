#property strict

// Event notified when general account information is changed.
class AccountChangedEvent {
public:
    string currency;
    int    leverage;
    double credit;
    bool   expert_allowed;
    bool   trade_allowed;
    int    max_active_orders;
};
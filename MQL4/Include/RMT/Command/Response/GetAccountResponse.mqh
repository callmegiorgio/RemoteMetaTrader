#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// {
///   "login":         integer,
///   "name":          string,
///   "server":        string,
///   "company":       string,
///   "tradeMode":     string,
///   "marginMode":    string,
///   "leverage":      integer,
///   "orderLimit":    integer,
///   "currency":      string,
///   "balance":       double,
///   "credit":        double,
///   "profit":        double,
///   "equity":        double,
///   "margin":        double,
///   "freeMargin":    double,
///   "marginLvl":     double,
///   "marginCallLvl": double,
///   "marginStopLvl": double,
///   "tradeAllowed":  bool,
///   "expertAllowed": bool
/// }
class GetAccountResponse {
public:
    void write(JsonWriter& writer) const
    {
        string trade_mode_str;
        string margin_mode_str;

        switch (this.trade_mode)
        {
            case ACCOUNT_TRADE_MODE_DEMO:    trade_mode_str = "demo";    break;
            case ACCOUNT_TRADE_MODE_REAL:    trade_mode_str = "real";    break;
            case ACCOUNT_TRADE_MODE_CONTEST: trade_mode_str = "contest"; break;
            default:
                trade_mode_str = "unknown";
        }

        switch (this.margin_mode)
        {
            case ACCOUNT_STOPOUT_MODE_PERCENT: margin_mode_str = "percent"; break;
            case ACCOUNT_STOPOUT_MODE_MONEY:   margin_mode_str = "money";   break;
            default:
                trade_mode_str = "unknown";
        }

        writer.write("login",         this.login);
        writer.write("name",          this.name);
        writer.write("server",        this.server);
        writer.write("company",       this.company);
        writer.write("tradeMode",     trade_mode_str);
        writer.write("marginMode",    margin_mode_str);
        writer.write("leverage",      this.leverage);
        writer.write("orderLimit",    this.order_limit);
        writer.write("currency",      this.currency);
        writer.write("balance",       this.balance);
        writer.write("credit",        this.credit);
        writer.write("profit",        this.profit);
        writer.write("equity",        this.equity);
        writer.write("margin",        this.margin);
        writer.write("freeMargin",    this.free_margin);
        writer.write("marginLvl",     this.margin_level);
        writer.write("marginCallLvl", this.margin_call_level);
        writer.write("marginStopLvl", this.margin_stop_level);
        writer.write("tradeAllowed",  this.trade_allowed);
        writer.write("expertAllowed", this.expert_allowed);
    }

    long   login;
    string name;
    string server;
    string company;
    long   leverage;
    int    order_limit;
    string currency;
    double balance;
    double credit;
    double profit;
    double equity;
    double margin;
    double free_margin;
    double margin_level;
    double margin_call_level;
    double margin_stop_level;
    bool   trade_allowed;
    bool   expert_allowed;

    ENUM_ACCOUNT_TRADE_MODE trade_mode;
    ENUM_ACCOUNT_STOPOUT_MODE margin_mode;
};
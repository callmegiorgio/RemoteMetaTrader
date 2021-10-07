#property strict

// Local
#include "../../Utility/JsonWriter.mqh"

/// Response:
/// {
///   "login":      integer,
///   "name":       string,
///   "server":     string,
///   "company":    string,
///   "mode":       string,
///   "leverage":   integer,
///   "orderLimit": integer,
///   "currency":   string,
///   "balance":    double,
///   "credit":     double,
///   "profit":     double,
///   "equity":     double,
///   "margin":     double,
///   "freeMargin": double,
///   "marginLvl":  double,
///   "canTrade":   bool,
///   "canExpert":  bool
/// }
class GetAccountResponse {
public:
    void write(JsonWriter& writer) const
    {
        string str_mode;

        switch (this.mode)
        {
            case ACCOUNT_TRADE_MODE_DEMO:    str_mode = "demo";    break;
            case ACCOUNT_TRADE_MODE_REAL:    str_mode = "real";    break;
            case ACCOUNT_TRADE_MODE_CONTEST: str_mode = "contest"; break;
            default:;
        }

        writer.write("login",      this.login);
        writer.write("name",       this.name);
        writer.write("server",     this.server);
        writer.write("company",    this.company);
        writer.write("mode",       str_mode);
        writer.write("leverage",   this.leverage);
        writer.write("orderLimit", this.order_limit);
        writer.write("currency",   this.currency);
        writer.write("balance",    this.balance);
        writer.write("credit",     this.credit);
        writer.write("profit",     this.profit);
        writer.write("equity",     this.equity);
        writer.write("margin",     this.margin);
        writer.write("freeMargin", this.free_margin);
        writer.write("marginLvl",  this.margin_level);
        writer.write("canTrade",   this.trade_allowed);
        writer.write("canExpert",  this.expert_allowed);
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
    bool   trade_allowed;
    bool   expert_allowed;

    ENUM_ACCOUNT_TRADE_MODE mode;
};
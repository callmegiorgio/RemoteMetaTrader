#property strict

class Account {
public:
    static int login();
    static string name();
    static string server();
    static string company();
    static string currency();
    static int leverage();
    static int max_active_orders();
    static bool is_trade_allowed();
    static bool is_expert_allowed();
    
    static ENUM_ACCOUNT_TRADE_MODE trade_mode();
    static ENUM_ACCOUNT_STOPOUT_MODE stop_out_mode();

    static double balance();
    static double credit();
    static double profit();
    static double equity();
    static double margin();
    static double free_margin();
    static double margin_level();
    static double margin_call_level();
    static double margin_stop_out_level();

private:
    Account() = delete;
};

static int Account::login()
{
    return AccountNumber();
}

static string Account::name()
{
    return AccountName();
}

static string Account::server()
{
    return AccountServer();
}

static string Account::company()
{
    return AccountCompany();
}

static string Account::currency()
{
    return AccountCurrency();
}

static int Account::leverage()
{
    return AccountLeverage();
}

static int Account::max_active_orders()
{
    return int(AccountInfoInteger(ACCOUNT_LIMIT_ORDERS));
}

static bool Account::is_trade_allowed()
{
    return bool(AccountInfoInteger(ACCOUNT_TRADE_ALLOWED));
}

static bool Account::is_expert_allowed()
{
    return bool(AccountInfoInteger(ACCOUNT_TRADE_EXPERT));
}

static ENUM_ACCOUNT_TRADE_MODE Account::trade_mode()
{
    return ENUM_ACCOUNT_TRADE_MODE(AccountInfoInteger(ACCOUNT_TRADE_MODE));
}

static ENUM_ACCOUNT_STOPOUT_MODE Account::stop_out_mode()
{
    return ENUM_ACCOUNT_STOPOUT_MODE(AccountInfoInteger(ACCOUNT_MARGIN_SO_MODE));
}

static double Account::balance()
{
    return AccountBalance();
}

static double Account::credit()
{
    return AccountCredit();
}

static double Account::profit()
{
    return AccountProfit();
}

static double Account::equity()
{
    return AccountEquity();
}

static double Account::margin()
{
    return AccountMargin();
}

static double Account::free_margin()
{
    return AccountFreeMargin();
}

static double Account::margin_level()
{
    return AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
}

static double Account::margin_call_level()
{
    return AccountInfoDouble(ACCOUNT_MARGIN_SO_CALL);
}

static double Account::margin_stop_out_level()
{
    return AccountInfoDouble(ACCOUNT_MARGIN_SO_SO);
}
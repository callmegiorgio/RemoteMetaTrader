#property strict

// Local
#include "../Trading/Account.mqh"
#include "../Utility/Observer.mqh"
#include "AccountChangedEvent.mqh"
#include "EquityUpdatedEvent.mqh"

class AccountEventSubject {
public:
    AccountEventSubject();

    void register(Observer<AccountChangedEvent>* observer);
    void register(Observer<EquityUpdatedEvent>* observer);

    void update();

private:
    Subject<AccountChangedEvent> m_account_changed_ev_sub;
    Subject<EquityUpdatedEvent>  m_equity_updated_ev_sub;

    string m_currency;
    int    m_leverage;
    double m_credit;
    bool   m_expert_allowed;
    bool   m_trade_allowed;
    int    m_max_active_orders;
    double m_equity;
    double m_balance;
};

AccountEventSubject::AccountEventSubject()
{
    m_currency          = Account::currency();
    m_leverage          = Account::leverage();
    m_credit            = Account::credit();
    m_expert_allowed    = Account::is_expert_allowed();
    m_trade_allowed     = Account::is_trade_allowed();
    m_max_active_orders = Account::max_active_orders();
    m_equity            = Account::equity();
    m_balance           = Account::balance();
}

void AccountEventSubject::register(Observer<AccountChangedEvent>* observer)
{
    m_account_changed_ev_sub.register(observer);
}

void AccountEventSubject::register(Observer<EquityUpdatedEvent>* observer)
{
    m_equity_updated_ev_sub.register(observer);
}

void AccountEventSubject::update()
{
    const bool account_changed = (
        (m_currency          != Account::currency())          ||
        (m_leverage          != Account::leverage())          ||
        (m_credit            != Account::credit())            ||
        (m_expert_allowed    != Account::is_expert_allowed()) ||
        (m_trade_allowed     != Account::is_trade_allowed())  ||
        (m_max_active_orders != Account::max_active_orders())
    );

    if (account_changed)
    {
        AccountChangedEvent ev;
        ev.currency          = m_currency          = Account::currency();
        ev.leverage          = m_leverage          = Account::leverage();
        ev.credit            = m_credit            = Account::credit();
        ev.expert_allowed    = m_expert_allowed    = Account::is_expert_allowed();
        ev.trade_allowed     = m_trade_allowed     = Account::is_trade_allowed();
        ev.max_active_orders = m_max_active_orders = Account::max_active_orders();

        m_account_changed_ev_sub.notify(ev);
    }

    if (m_equity != Account::equity())
    {
        EquityUpdatedEvent ev;
        ev.equity = m_equity = Account::equity();
        ev.profit            = Account::profit();
        ev.margin            = Account::margin();
        ev.margin_level      = Account::margin_level();
        ev.free_margin       = Account::free_margin();

        if (m_balance != Account::balance())
            ev.balance = m_balance = Account::balance();

        m_equity_updated_ev_sub.notify(ev);
    }
}
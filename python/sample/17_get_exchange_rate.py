import rmt

mt4 = rmt.exchanges.MetaTrader4()

def print_rate(base_currency: str, quote_currency: str):
    try:
        rate = mt4.get_exchange_rate(base_currency, quote_currency)

        print('{0}{1} -> {2}'.format(base_currency, quote_currency, rate))
    except rmt.error.RMTError as e:
        print(str(e))

print('Account currency:', mt4.account.currency)

currencies = ['USD', 'EUR', 'GBP', 'AUD', 'JPY', 'NZD', 'CHF', 'BRL', 'JPY']

currencies_len = len(currencies)

for base_currency in currencies:
    for quote_currency in currencies:
        print_rate(base_currency, quote_currency)
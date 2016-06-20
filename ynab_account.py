from ynab import YNAB
import json

balance = dict()

ynab = YNAB('~/Dropbox/YNAB', 'My Budget')

balance['HDFC CC'] = ynab.accounts['HDFC CC'].balance
balance['HDFC Savings'] = ynab.accounts['HDFC Savings'].balance

print json.dumps(balance, indent=2)

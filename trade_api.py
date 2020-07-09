import os
from config import *
from coinbase.wallet.client import Client

if DEBUG:
	from fake_trade_api import *
else:
	class TradeAPI(object):
		def __init__(self):
			self.client = Client(COINBASE_API_KEY, COINBASE_SECRET_KEY)
			self.crypto_account = self.client.get_account(CRYPTO_CURRENCY)
			self.fiat_account = self.client.get_account(FIAT_CURRENCY)
			self.payment_method = next(payment_method for payment_method in self.client.get_payment_methods(limit=100).data if payment_method.type == "fiat_account" and payment_method.fiat_account.id == self.fiat_account.id)

		def get_crypto_balance(self):
			self.crypto_account.refresh()
			crypto_balance = Decimal(self.crypto_account.balance.amount)
			if crypto_balance == 0:
				return 0.0

			exchange_rate = Decimal(self.client.get_sell_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)
			return crypto_balance * exchange_rate

		def get_fiat_balance(self):
			self.fiat_account.refresh()
			return Decimal(self.fiat_account.balance.amount)

		def get_total_balance(self):
			return self.get_fiat_balance() + self.get_crypto_balance()

		def get_crypto_ratio(self):
			self.crypto_account.refresh()
			self.fiat_account.refresh()

			crypto_balance = Decimal(self.crypto_account.balance.amount)
			fiat_balance = Decimal(self.fiat_account.balance.amount)

			if crypto_balance == 0:
				return Decimal("0")
			elif fiat_balance == 0:
				return Decimal("1")

			exchange_rate = Decimal(self.client.get_spot_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)

			crypto_in_fiat = crypto_balance * exchange_rate
			return crypto_in_fiat / (crypto_in_fiat + fiat_balance)

		def get_delta_to_ratio(self):
			self.crypto_account.refresh()
			self.fiat_account.refresh()

			crypto_balance = Decimal(self.crypto_account.balance.amount)
			fiat_balance = Decimal(self.fiat_account.balance.amount)

			if crypto_balance == 0 and fiat_balance == 0:
				return Decimal("0")

			exchange_rate = Decimal(self.client.get_spot_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)
			crypto_in_fiat = crypto_balance * exchange_rate

			target = (crypto_in_fiat + fiat_balance) * exchange_rate
			return target - crypto_in_fiat

		def buy_crypto(self, fiat_amount):
			self.client.buy(self.crypto_account.id, total=fiat_amount, currency=self.fiat_account.currency, payment_method=self.payment_method.id)

		def sell_crypto(self, fiat_amount):
			self.client.sell(self.crypto_account.id, amount=fiat_amount, currency=self.fiat_account.currency, payment_method=self.payment_method.id)

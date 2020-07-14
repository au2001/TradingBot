import os
from math import ceil
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

		def get_delta_to_ratio(self, ratio):
			self.crypto_account.refresh()
			self.fiat_account.refresh()

			crypto_balance = Decimal(self.crypto_account.balance.amount)
			fiat_balance = Decimal(self.fiat_account.balance.amount)

			if crypto_balance == 0 and fiat_balance == 0:
				return Decimal("0")

			exchange_rate = Decimal(self.client.get_spot_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)
			crypto_in_fiat = crypto_balance * exchange_rate
			current = crypto_in_fiat / (crypto_in_fiat + fiat_balance)

			if ratio == current:
				delta = 0

			elif ratio > current: # Buy
				buy_price = Decimal(self.client.get_buy_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)

				# ratio = (crypto_in_fiat + (delta - fee) / buy_price * exchange_rate) / (crypto_in_fiat + (delta - fee) / buy_price * exchange_rate + fiat_balance - delta)
				# delta = (fiat_balance * buy_price * ratio + crypto_in_fiat * buy_price * (ratio - 1) - fee * (ratio - 1) * exchange_rate) / (buy_price * ratio + exchange_rate * (1 - ratio))
				delta = (fiat_balance * buy_price * ratio + crypto_in_fiat * buy_price * (ratio - 1)) / (buy_price * ratio + exchange_rate * (1 - ratio)) # - fee * (ratio - 1) * exchange_rate / (buy_price * ratio + exchange_rate * (1 - ratio))

				fee = 0
				fee_multiplier = - (ratio - 1) * exchange_rate / (buy_price * ratio + exchange_rate * (1 - ratio))
				while True:
					new_fee = Decimal(self.estimate_fee(delta + fee)) * fee_multiplier
					if delta < 0:
						new_fee *= -1

					if fee == new_fee:
						break
					fee = new_fee
				delta += fee

			else: # Sell
				sell_price = Decimal(self.client.get_sell_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)

				# ratio = (crypto_in_fiat - delta / sell_price * exchange_rate) / (crypto_in_fiat - delta / sell_price * exchange_rate + fiat_balance + delta - fee)
				# delta = sell_price * (ratio * (fee - fiat_balance) + crypto_in_fiat * (1 - ratio)) / (sell_price * ratio + (1 - ratio) * exchange_rate)
				delta = sell_price * (crypto_in_fiat * (1 - ratio) - fiat_balance * ratio) / (sell_price * ratio + (1 - ratio) * exchange_rate) # + fee * ratio * sell_price / (sell_price * ratio + (1 - ratio) * exchange_rate)

				fee = 0
				fee_multiplier = ratio * sell_price / (sell_price * ratio + (1 - ratio) * exchange_rate)
				while True:
					new_fee = Decimal(self.estimate_fee(delta + fee)) * fee_multiplier
					if delta < 0:
						new_fee *= -1

					if fee == new_fee:
						break
					fee = new_fee
				delta += fee
				delta *= -1

			return Decimal(delta)

		def estimate_fee(self, fiat_amount):
			if fiat_amount <= 10:
				flat_fee = Decimal("0.99")
			elif fiat_amount <= 25:
				flat_fee = Decimal("1.49")
			elif fiat_amount <= 50:
				flat_fee = Decimal("1.99")
			elif fiat_amount <= 200:
				flat_fee = Decimal("2.99")
			else:
				flat_fee = Decimal("0.0")

			variable_fee = fiat_amount * COINBASE_VARIABLE_FEE
			return Decimal(max(flat_fee, variable_fee))

		def buy_crypto(self, fiat_amount):
			return self.client.buy(self.crypto_account.id, total=float(fiat_amount), currency=self.fiat_account.currency, payment_method=self.payment_method.id)

		def sell_crypto(self, fiat_amount):
			return self.client.sell(self.crypto_account.id, amount=float(fiat_amount), currency=self.fiat_account.currency, payment_method=self.payment_method.id)

import os
from math import ceil
from decimal import Decimal
from config import *
from coinbase.wallet.client import Client

class TradeAPI(object):
	def __init__(self):
		self.client = Client(COINBASE_API_KEY, COINBASE_SECRET_KEY)
		self.crypto_multiplier = Decimal("100000000")
		self.crypto_balance = Decimal("0") * self.crypto_multiplier
		self.fiat_multiplier = Decimal("100")
		self.fiat_balance = Decimal("100") * self.fiat_multiplier

	def get_exchange_rate(self):
		return Decimal(self.client.get_spot_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)

	def get_sell_price(self, exchange_rate=None):
		if exchange_rate is not None:
			return exchange_rate * Decimal("0.99")

		return Decimal(self.client.get_sell_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)

	def get_buy_price(self, exchange_rate=None):
		if exchange_rate is not None:
			return exchange_rate * Decimal("1.01")

		return Decimal(self.client.get_buy_price(currency_pair=CRYPTO_CURRENCY + "-" + FIAT_CURRENCY).amount)

	def get_crypto_balance(self, sell_price=None, exchange_rate=None):
		if self.crypto_balance == 0:
			return Decimal("0")

		if sell_price is None:
			sell_price = self.get_sell_price(exchange_rate=exchange_rate)

		return self.crypto_balance / self.crypto_multiplier * sell_price

	def get_fiat_balance(self):
		return self.fiat_balance / self.fiat_multiplier

	def get_total_balance(self, buy_price=None, sell_price=None, exchange_rate=None):
		return self.get_fiat_balance() + self.get_crypto_balance(sell_price=sell_price, exchange_rate=exchange_rate)

	def get_crypto_ratio(self, exchange_rate=None):
		if self.crypto_balance == 0:
			return Decimal("0")
		elif self.fiat_balance == 0:
			return Decimal("1")

		if exchange_rate is None:
			exchange_rate = self.get_exchange_rate()

		crypto_in_fiat = int(self.crypto_balance / self.crypto_multiplier * exchange_rate * self.fiat_multiplier)
		return crypto_in_fiat / (crypto_in_fiat + self.fiat_balance)

	def get_delta_to_ratio(self, exchange_rate=None):
		if self.crypto_balance == 0 and self.fiat_balance == 0:
			return Decimal("0")

		if exchange_rate is None:
			exchange_rate = self.get_exchange_rate()
		crypto_in_fiat = self.crypto_balance / self.crypto_multiplier * exchange_rate * self.fiat_multiplier

		target = (crypto_in_fiat + self.fiat_balance) * exchange_rate
		return (target - crypto_in_fiat) / self.fiat_multiplier

	def get_fee(self, fiat_amount):
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
		return max(flat_fee, variable_fee)

	def buy_crypto(self, fiat_amount, buy_price=None, exchange_rate=None):
		fiat_amount = Decimal(int(fiat_amount * self.fiat_multiplier)) / self.fiat_multiplier
		if ceil(fiat_amount * self.fiat_multiplier) > self.fiat_balance:
			raise Exception("Amount exceeds balance.")

		if buy_price is None:
			buy_price = self.get_buy_price(exchange_rate=exchange_rate)

		fee = self.get_fee(fiat_amount)
		crypto_amount = (fiat_amount - fee) / buy_price

		self.fiat_balance -= int(fiat_amount * self.fiat_multiplier)
		self.crypto_balance += int(crypto_amount * self.crypto_multiplier)

	def sell_crypto(self, fiat_amount, sell_price=None, exchange_rate=None):
		if sell_price is None:
			sell_price = self.get_sell_price(exchange_rate=exchange_rate)

		fiat_amount = Decimal(int(fiat_amount * self.fiat_multiplier)) / self.fiat_multiplier
		crypto_amount = fiat_amount / sell_price

		if ceil(crypto_amount * self.crypto_multiplier) > self.crypto_balance:
			raise Exception("Amount exceeds balance.")

		fee = self.get_fee(fiat_amount)

		self.crypto_balance -= int(crypto_amount * self.crypto_multiplier)
		self.fiat_balance += int((fiat_amount - fee) * self.fiat_multiplier)

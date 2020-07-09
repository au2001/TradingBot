import json
import requests
from time import time
from datetime import datetime
from urllib.parse import quote_plus
from config import *

class PriceAPI(object):
	def __init__(self):
		self.api_url = "https://min-api.cryptocompare.com/data/v2/"
		self.api_key = CRYPTOCOMPARE_API_KEY

		self.cache = None
		self.download_cache()

	def get(self, endpoint, **kwargs):
		query = []
		for key, value in kwargs.items():
			if value is None:
				continue

			query.append(quote_plus(str(key)) + "=" + quote_plus(str(value)))

		if query:
			query = "?" + "&".join(query)

		url = self.api_url + endpoint + query
		result = requests.get(url, headers={
			"Authorization": "Apikey " + self.api_key
		}).json()
		return result

	def download_cache(self):
		if self.cache is None:
			try:
				with open("cache.json", "r") as f:
					self.cache = json.load(f)
			except FileNotFoundError:
				self.cache = []

		oldest = self.cache[-1]['time'] if self.cache else 1420070400 # Jan 1st, 2015
		current = int(time() / (60 * 60)) * 60 * 60

		if oldest >= current:
			print("Cache up to date!")
			return

		while oldest < current:
			oldest += 2000 * 60 * 60
			result = self.get("histohour", fsym=CRYPTO_CURRENCY, tsym=FIAT_CURRENCY, limit=2000, toTs=oldest)
			assert result['Response'] == "Success"
			self.cache += sorted(result['Data']['Data'], key=lambda x: x['time'])
			print("Downloaded cache up to:", datetime.fromtimestamp(self.cache[-1]['time']).strftime("%Y/%m/%d %H:%M"))

		with open("cache.json", "w") as f:
			json.dump(self.cache, f)

	def get_history(self, from_timestamp=None, to_timestamp=None):
		limit, interval = 2000, 60 * 60
		if to_timestamp is None and from_timestamp is None:
			to_timestamp = int(time() / interval) * interval
			from_timestamp = to_timestamp - (limit - 1) * interval
		elif to_timestamp is None:
			from_timestamp = int(from_timestamp / interval) * interval
			to_timestamp = from_timestamp + (limit - 1) * interval
		elif from_timestamp is None:
			to_timestamp = int(to_timestamp / interval) * interval
			from_timestamp = to_timestamp - (limit - 1) * interval
		else:
			from_timestamp = int(from_timestamp / interval) * interval
			to_timestamp = int(to_timestamp / interval) * interval
			limit = (to_timestamp - from_timestamp) // interval

		a, b = 0, len(self.cache)
		while a < b - 1:
			mid = (a + b) // 2
			if to_timestamp == self.cache[mid]['time']:
				a, b = mid, mid + 1
			elif to_timestamp > self.cache[mid]['time']:
				a = mid + 1
			else:
				b = mid

		max_index = b
		min_index = max(max_index - limit, 0)

		history = self.cache[min_index:max_index]
		history = list(map(lambda x: Decimal(str(x['close'])), history))
		return history

import requests
from time import time
from urllib.parse import quote_plus
from config import *

if DEBUG:
	from fake_price_api import *
else:
	class PriceAPI(object):
		def __init__(self):
			self.api_url = "https://min-api.cryptocompare.com/data/v2/"
			self.api_key = CRYPTOCOMPARE_API_KEY

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

			result = self.get("histohour", fsym=CRYPTO_CURRENCY, tsym=FIAT_CURRENCY, limit=limit, toTs=to_timestamp)
			assert result['Response'] == "Success"

			history = sorted(result['Data']['Data'], key=lambda x: x['time'])
			history = list(map(lambda x: Decimal(str(x['close'])), history))
			return history

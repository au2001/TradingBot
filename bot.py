from random import randrange
from config import *
from price_api import PriceAPI
from trade_api import TradeAPI
from artificial_intelligence import Network

def evaluator(price_api):
	def evaluate(networks):
		states = [(TradeAPI(), network) for network in networks]
		index = randrange(2000, len(price_api.cache) - 30 * 24 - 1)

		for offset in range(0, 30 * 24, 24): # TODO: Test every hour
			to_timestamp = price_api.cache[index + offset]['time']
			history = price_api.get_history(to_timestamp=to_timestamp)

			exchange_rate = Decimal(str(price_api.cache[index + offset + 1]['close']))

			for trade_api, network in states:
				ratio = trade_api.get_crypto_ratio(exchange_rate=exchange_rate)
				action = network.predict(ratio, history)
				network.take_action(action, trade_api, exchange_rate=exchange_rate)

		return list(map(lambda x: (x[0].get_total_balance(exchange_rate=exchange_rate), x[1]), states))

	return evaluate

def main():
	price_api = PriceAPI()

	if DEBUG and TRAIN:
		print("Training model, please wait...")
		evaluate = evaluator(price_api)
		network = Network.train(evaluate)
		network.save()

		print("Evaluating model, please wait...")
		score = evaluate([network])[0][0]
		print("Predicted yield over 30 days: %.2f%%" % (score - 100))
	else:
		network = Network()
		network.load()

	trade_api = TradeAPI()
	ratio = trade_api.get_crypto_ratio()
	history = price_api.get_history()

	action = network.predict(ratio, history)

	print("Investing %d%% in cryptocurrency..." % (action / (network.brackets_count - 1) * 100))
	network.take_action(action, trade_api)

	crypto_balance = trade_api.get_crypto_balance()
	fiat_balance = trade_api.get_fiat_balance()

	print("New balance:")
	print("", "Crypto:", "%12.2f" % crypto_balance, sep="\t")
	print("", "Fiat:", "%12.2f" % fiat_balance, sep="\t")
	print("", "Total:", "%12.2f" % (crypto_balance + fiat_balance), sep="\t")
	print("", "Ratio:", "%12.2f%%" % (trade_api.get_crypto_ratio() * 100), sep="\t")

if __name__ == "__main__":
	main()

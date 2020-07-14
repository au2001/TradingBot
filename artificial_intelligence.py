import numpy as np
from math import sqrt
from decimal import Decimal
from keras.models import Sequential
from keras.layers import Dense

class Network(object):
	def __init__(self, brackets_count=5):
		self.brackets_count = brackets_count

		self.model = Sequential()
		self.model.add(Dense(12, input_dim=brackets_count + 2000, activation="relu"))
		self.model.add(Dense(8, activation="relu"))
		self.model.add(Dense(8, activation="relu"))
		self.model.add(Dense(brackets_count, activation="softmax"))

	def breed_and_mutate(networks, children_count):
		children = [Network() for _ in range(children_count)]

		if len(networks) == 1:
			for child in children:
				child.model.set_weights(networks[0][1].model.get_weights())
		elif len(networks) > 1:
			parent_networks = np.array(list(map(lambda x: x[1], networks)))
			scores = np.array(list(map(lambda x: x[0], networks)), dtype=float)
			scores /= np.sum(scores)

			for child in children:
				parent_a, parent_b = np.random.choice(parent_networks, 2, p=scores, replace=False)
				weights = parent_a.model.get_weights()
				weights_b = parent_b.model.get_weights()
				for i in range(len(weights)):
					weights[i] = (weights[i] + weights_b[i]) / 2
				child.model.set_weights(weights)

		for child in children:
			weights = child.model.get_weights()
			for i in range(len(weights)):
				average = np.sum(abs(weights[i])) / weights[i].size
				weights[i] += np.random.rand(*weights[i].shape) * average * 0.1
			child.model.set_weights(weights)

		return children

	def train(evaluator):
		network = Network()
		network.load()
		best_network = (0, network)
		networks = [best_network]

		for epoch in range(1, 11):
			print("Training... Epoch", epoch)
			networks = evaluator(Network.breed_and_mutate(networks, 10))

			for i in range(1, len(networks)):
				if networks[i][0] > best_network[0]:
					best_network = networks[i]

		print("Finished traning. Using best model so far.")

		return best_network[1]

	def load(self):
		try:
			self.model.load_weights("model.h5")
		except OSError:
			pass

	def save(self):
		self.model.save_weights("model.h5")

	def predict(self, ratio, history):
		history_length = len(history)
		average = sum(history) / history_length

		standard_history, variance = [], 0
		for tick in history:
			tick -= average
			variance += tick * tick
			standard_history.append(tick)

		variance = sqrt(variance / history_length)
		for i in range(history_length):
			standard_history[i] = float(standard_history[i] / Decimal(variance))

		brackets = [0] * self.brackets_count
		brackets[int(ratio * (self.brackets_count - 1) + Decimal("0.5"))] = 1

		return int(np.argmax(self.model.predict([brackets + standard_history]), axis=-1)[0])

	def take_action(self, action, trade_api, exchange_rate=None):
		delta = trade_api.get_delta_to_ratio(Decimal(action) / Decimal(self.brackets_count - 1), exchange_rate=exchange_rate)
		if delta >= 2: # No transactions of less than $2
			trade_api.buy_crypto(delta)
		elif delta <= -2: # No transactions of less than $2
			trade_api.sell_crypto(-delta)

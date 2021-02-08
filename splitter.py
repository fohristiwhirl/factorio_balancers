import random, statistics

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
test_length = 10000
max_traversal = 10000

class Thing:

	def __init__(self, name, *, root = False, terminus = False):
		self.name = name
		self.root = root
		self.terminus = terminus
		self.reset()

	def reset(self):
		self.selectindex = 0
		self.ins = []
		self.outs = []

	def select(self):
		if self.outputs() == 0:
			raise IndexError
		elif self.outputs() == 1:
			return self.outs[0]
		else:
			ret = self.outs[self.selectindex]
			self.selectindex = (self.selectindex + 1) % 2
			return ret

	def connect(self, other):

		if self.outputs() + 1 > self.max_outputs():
			return False

		if other.inputs() + 1 > other.max_inputs():
			return False

		self.outs.append(other)
		other.ins.append(self)
		return True

	def inputs(self):
		return len(self.ins)

	def outputs(self):
		return len(self.outs)

	def free_inputs(self):
		return self.max_inputs() - len(self.ins)

	def free_outputs(self):
		return self.max_outputs() - len(self.outs)

	def max_inputs(self):
		if self.root:
			return 0
		elif self.terminus:
			return 1
		else:
			return 2

	def max_outputs(self):
		if self.root:
			return 1
		elif self.terminus:
			return 0
		else:
			return 2

	def print(self):

		if self.outputs() == 0:
			print("{} (no outputs)".format(self.name))
			return

		print("{} --> {}".format(self.name, self.outs[0].name))

		if self.outputs() == 2:
			print("{} --> {}".format(" " * len(self.name), self.outs[1].name))


def main():

	root_count = int(input("How many input belts? "))
	splitter_count = int(input("How many splitters to use? "))
	terminus_count = int(input("How many output belts? "))

	roots = []
	splitters = []
	termini = []

	for n in range(root_count):
		roots.append(Thing("Root {}".format(n + 1), root = True))

	for n in range(splitter_count):
		splitters.append(Thing("Splitter {}".format(alphabet[n])))

	for n in range(terminus_count):
		termini.append(Thing("(Terminus {})".format(n + 1), terminus = True))

	best_variance = None

	print("-------------------------------------------------------------------")
	print("Searching...", end="", flush=True)

	while 1:

		# For each run, generate the probability that a splitter will have 2 outputs...

		two_output_chance = random.random()

		# Reset all objects...

		for lst in [roots, splitters, termini]:
			for item in lst:
				item.reset()

		# Attach roots...

		for root in roots:
			while 1:
				if root.connect(random.choice(splitters)):
					break

		# Attach termini...

		for terminus in termini:
			while 1:
				source = random.choice(splitters)
				if source.connect(terminus):
					break

		# Attach splitters...

		success = True

		for splitter in splitters:

			if random.random() < two_output_chance:
				num_outputs = 2
			else:
				num_outputs = 1

			for n in range(num_outputs):

				for i in range(50):
					if splitter.connect(random.choice(splitters)):
						break

			if splitter.outputs() == 0:
				success = False
				break

		if not success:
			continue

		scores = get_scores(roots, splitters, termini)

		if scores is None:
			continue

		pvar = statistics.pvariance(scores)

		if best_variance == None or pvar < best_variance:

			best_variance = pvar

			print("\b" * len("Searching..."), end="", flush=True)

			for root in roots:
				root.print()

			for splitter in splitters:
				splitter.print()

			print(scores)

			print("-------------------------------------------------------------------")
			print("Searching...", end="", flush=True)


def get_scores(roots, splitters, termini):

	scores = [0 for terminus in termini]

	for n in range(test_length):

		steps = 0

		o = roots[n % len(roots)]

		while not o.terminus:
			o = o.select()
			steps += 1
			if steps > max_traversal:
				return None

		for i, terminus in enumerate(termini):
			if o is terminus:
				scores[i] += 1
				break

	return scores


if __name__ == "__main__":
	main()

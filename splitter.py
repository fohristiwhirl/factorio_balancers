import copy, random, statistics

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

	def reset_selector(self):
		self.selectindex = 0

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

	def disconnect_inputs(self):
		for source in copy.copy(self.ins):
			source.outs.remove(self)
			self.ins.remove(source)

	def disconnect_outputs(self):
		for target in copy.copy(self.outs):
			self.outs.remove(target)
			target.ins.remove(self)

	def inputs(self):
		return len(self.ins)

	def outputs(self):
		return len(self.outs)

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
		if (not self.root) and self.inputs() == 0:
			print("{} (x)".format(self.name))
			return
		if (not self.terminus) and self.outputs() == 0:
			print("{} (no outputs)".format(self.name))		# should never be
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
		termini.append(Thing("--------->".format(n + 1), terminus = True))

	best_variance = None

	print("-------------------------------------------------------------------")
	print("Searching...", end="", flush=True)

	while 1:

		# For each run, generate the probability that a splitter will try to add 2 outputs at the final phase...

		two_output_chance = random.random()

		# Reset all objects...

		for lst in [roots, splitters, termini]:
			for item in lst:
				item.reset()

		# Attach roots...

		for root in roots:

			if root.name == "Root 1":
				root.connect(splitters[0])
			else:
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
				extra_outputs = 2
			else:
				extra_outputs = 1

			for n in range(extra_outputs):

				# Since some outputs may already be connected to termini, we might not actually be able to add...

				if splitter.outputs() == 2:
					break

				for i in range(50):
					target = random.choice(splitters)
					if target in splitter.outs:			# don't connect to the same thing twice
						continue
					if splitter.connect(target):
						break

			if splitter.outputs() == 0:
				success = False
				break

		if not success:
			continue

		# Run test...

		scores = get_scores(roots, splitters, termini)

		if scores == None:
			continue

		pvar = statistics.pvariance(scores)

		if best_variance == None or pvar < best_variance:

			best_variance = pvar

			print("\b" * len("Searching..."), end="", flush=True)

			normalise(splitters)

			# As a sanity check, test the network again.
			# Note that there might sometimes be a slight difference caused by index positions changing.

			scores2 = get_scores(roots, splitters, termini)
			if scores != scores2:
				print("WARNING: score divergence after normalisation:")
				print("{}; {}".format(scores, scores2))

			for root in roots:
				root.print()

			for splitter in splitters:
				splitter.print()

			print(scores)

			print("-------------------------------------------------------------------")
			print("Searching...", end="", flush=True)


def normalise(splitters):

	while 1:

		changes = False

		# Fully disconnect any splitters with no inputs:

		for splitter in splitters:
			if splitter.inputs() == 0 and splitter.outputs() > 0:
				splitter.disconnect_outputs()
				changes = True

		# If a splitter has 1 input and 1 output, it does nothing, just connect the things:

		for splitter in splitters:

			if splitter.inputs() == 1 and splitter.outputs() == 1:

				if splitter.outs[0] == splitter:		# it's only connecting to itself.
					splitter.disconnect_outputs()

				else:
					source = splitter.ins[0]
					target = splitter.outs[0]
					splitter.disconnect_inputs()
					splitter.disconnect_outputs()

					if not source.connect(target):
						raise AssertionError

				changes = True

		if not changes:
			return


def get_scores(roots, splitters, termini):

	for splitter in splitters:
		splitter.reset_selector()

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

from typing import Generic, TypeVar
from src.NFA import NFA, Transition, NodeGraph
import collections

S = TypeVar("S")
T = TypeVar("T")


class DFA(Generic[S]):
	def __init__(self, nfa):
		self.nfa = nfa
		self.graph = None
		self.state_number = 0
		self.sink = NodeGraph(-1, False, False)

	def xNext(self, state: NodeGraph, letter: str):
		current_state: Transition
		for current_state in state.adj:
			if current_state.transition == letter:
				return current_state.node

		return self.sink

	def xNextx(self, current_state: NodeGraph, input_char: str) -> NodeGraph:
		next_state = self.sink

		for transition in current_state.adj:
			if transition.transition == input_char:
				next_state = transition.node
				break
		return next_state

	def getStates(self) -> 'set[S]':
		pass

	def accepts(self, string: str) -> bool:
		"""
		@param string: String to check.
		@return: Returns true if the string is accepted and false if it is not.
		"""
		current_state = self.graph
		while len(string) != 0:
			current_state = self.xNext(current_state, string[0])
			string = string[1:]
		if current_state.is_final_state:
			return True
		return False

	def isFinal(self, state: S) -> bool:
		pass

	@staticmethod
	def fromPrenex(string: str) -> 'DFA[int]':
		"""
		@param string: Prenex.
		@return: Returns an DFA according to the prenex.
		"""
		nfa = NFA.fromPrenex(string)
		a = DFA(nfa)
		a.DFA_Graph()

		return a

	@staticmethod
	def fromNFA(nfa: NFA):
		"""
		@param nfa: NFA.
		@return: Returns DFA from NFA.
		"""
		a = DFA(nfa)
		a.DFA_Graph()

		return a

	def get_epsilon_states(self, state: NodeGraph, res=None) -> list[NodeGraph]:
		"""
		@param state: The initial state.
		@param res: The list of states to which the states on epsilon transitions will be added
		@return: Returns all states that can be reached from the current state by epsilon transitions. The method goes
		recursively on all epsilon transitions from the resulting states.
		"""
		if res is None:
			res = []
		res.append(state)
		for transition in state.adj:
			if transition.transition == "eps" and (transition.node not in res):
				self.get_epsilon_states(transition.node, res)
		return res

	@staticmethod
	def check_adj(state: NodeGraph, letter):
		"""
		@param state: The state for which the letter transition is sought.
		@param letter: The transition on the letter.
		@return: Returns true if the state "state" has no transition on the letter "letter", otherwise it returns false.
		"""
		for transition in state.adj:
			if transition.transition == letter:
				return False
		return True

	@staticmethod
	def check_if_visited(visited, states):
		"""

		@param visited: List of visited states.
		@param states: List of states.
		@return: This function checks whether a list of states (states) has already been visited or not.
		"""
		for j in visited:
			if collections.Counter(j.states) == collections.Counter(states):
				return True
		return False

	@staticmethod
	def is_start_state(node: NodeGraph):
		"""
		@param node: The state for which it is checked if it is initial.
		@return: Check if at least one state from the state list of the node is the initial state. Since the DFA
		consists of several states of the NFA, if at least one is the initial state, then the state in the DFA will also
		be initial.
		"""
		for state in node.states:
			if state.is_start_state:
				return True
		return False

	@staticmethod
	def is_final_state(node: NodeGraph):
		"""

		@param node: The state for which it is checked if it is final.
		@return: Check if at least one state from the state list of the node is the final state. Since the DFA
		consists of several states of the NFA, if at least one is the final state, then the state in the DFA will also
		be final.
		"""
		for state in node.states:
			if state.is_final_state:
				return True
		return False

	@staticmethod
	def is_lexer(node: NodeGraph, current_node: NodeGraph):
		for state in node.states:
			if state.lex != "":
				if current_node.lex == "":
					current_node.lex = state.lex
					current_node.lex_rank = state.lex_rank
				elif current_node.lex_rank > state.lex_rank:
					current_node.lex = state.lex
					current_node.lex_rank = state.lex_rank

	def DFA_Graph(self):
		# Add to the initial state from dfa all the states from nfa that can be traversed by epsilon transitions from
		# the initial state.
		current_state = self.get_epsilon_states(self.nfa.graph, [])
		# The first state of the dfa with the number 0 is created.
		graph = NodeGraph(self.state_number, False, False)
		self.state_number += 1
		graph.add_states(current_state)
		visited = []
		to_visit = [graph]
		while len(to_visit) > 0:
			# The current state is deleted from to_visit and added to visited.
			current_state = to_visit.pop()
			visited.append(current_state)
			# All the letters of the alphabet are scrolled.
			for letter in self.nfa.alphabet:
				states_per_letter = set()
				# For all the states in nfa from which the state in dfa is formed.
				for states in current_state.states:
					# Add to states_per_letter all the states we can reach from the states in nfa that make up the state
					# in dfa per letter "letter".
					for adj_states in states.adj:
						if adj_states.transition == letter:
							states_per_letter.add(adj_states.node)
					aux = set()
					# The states on epsilon transitions from each of the states found are also added.
					for i in states_per_letter:
						tmp = (self.get_epsilon_states(i, []))
						aux.update(tmp)
					states_per_letter.update(aux)

					if len(states_per_letter) == 0:
						# If none of the states in nfa from which the state in dfa is made up has a letter transition,
						# then the current state in dfa will have a transition to sink.
						if states == list(current_state.states)[len(current_state.states) - 1] and self.check_adj(current_state, letter):
							current_state.insert_graph(self.sink, letter)
					elif states == list(current_state.states)[len(current_state.states) - 1]:
						# If the newly formed state that should be in dfa has neither been visited nor should be visited,
						# then the new state is created and added to to_visit.
						if not self.check_if_visited(visited, states_per_letter) and states_per_letter not in to_visit:
							new_state = NodeGraph(self.state_number, False, False)
							new_state.add_states(states_per_letter)
							self.state_number += 1
							to_visit.append(new_state)
							current_state.insert_graph(new_state, letter)
						else:
							# A transition is created for the new state formed for dfa on the letter "letter".
							for j in visited:
								if collections.Counter(j.states) == collections.Counter(states_per_letter):
									current_state.insert_graph(j, letter)
		# Set the state in dfa if it is start state or end state.
		for state in visited:
			state.is_start_state = self.is_start_state(state)
			state.is_final_state = self.is_final_state(state)
			self.is_lexer(state, state)
		visited.append(self.sink)
		self.graph = visited[0]

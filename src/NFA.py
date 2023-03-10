from typing import Generic, TypeVar, Optional

S = TypeVar("S")
T = TypeVar("T")


class NodeTree:
    def __init__(self, data, right, left):
        self.left = left
        self.right = right
        self.data = data


class NodeGraph:
    def __init__(self, state_number, is_start_state, is_final_state):
        self.state_number = state_number
        self.states = []
        self.adj = []
        self.is_start_state = is_start_state
        self.is_final_state = is_final_state
        self.start_state = None
        self.final_state = None
        if is_start_state:
            self.start_state = self
        if is_final_state:
            self.final_state = self
        self.lex = ""
        self.lex_rank = -1

    def insert_graph(self, node, transition):
        """
        Add a new transition for the node self.
        @param node: The node on which the transition is passed.
        @param transition: Transition.
        """
        self.adj.append(Transition(node, transition))

    def update_final_state(self, node):
        """
        For each node in the graph, the final state is recursively updated.
        @param node: Final state node.
        """
        if self.final_state != node.final_state:
            self.final_state = node.final_state
            for i in range(len(self.adj)):
                self.adj[i].node.update_final_state(node)
        else:
            return

    def update_start_state(self, node):
        """
        For each node in the graph, the start state is recursively updated.
        @param node: Start state node.
        """
        if self.start_state != node.start_state:
            self.start_state = node.start_state
            for i in range(len(self.adj)):
                self.adj[i].node.update_start_state(node)
        else:
            return

    def add_states(self, states):
        """
        Set a list of states.
        @param states: List of states.
        """
        self.states = states


class Transition:
    def __init__(self, node: NodeGraph, transition):
        self.node = node
        self.transition = transition


class NFA(Generic[S]):

    def __init__(self, tree):
        self.state_number = 0
        self.alphabet = []
        self.states = set()
        self.graph = self.NFA_Graph(tree)

    def getStates(self) -> 'set[S]':
        """
        @return: The list of all states in nfa.
        """
        return self.states

    def accepts(self, string: str) -> bool:
        """
        @param string: String to check.
        @return: Returns true if the string is accepted and false if it is not.
        """
        return self._accept(string, self.graph)

    def _accept(self, string: str, graph: NodeGraph) -> bool:
        """Internal function used to check recursive"""
        if string == "" and graph.is_final_state:
            return True
        if string != "":
            mylist = []
            for i in range(len(graph.adj)):
                if graph.adj[i].transition == string[0]:
                    mylist.append(graph.adj[i].node)
            mylist = list(dict.fromkeys(mylist))
            for i in range(len(mylist)):
                if self._accept(string[1:], mylist[i]):
                    return True
        mylist = []
        for i in range(len(graph.adj)):
            if graph.adj[i].transition == "eps":
                mylist.append(graph.adj[i].node)
        mylist = list(dict.fromkeys(mylist))

        for i in range(len(mylist)):
            if self._accept(string, mylist[i]):
                return True
        return False

    def isFinal(self, state: S) -> bool:
        pass

    @staticmethod
    def fromPrenex(string: str) -> 'NFA[int]':
        """
        @param string: Prenex.
        @return: Returns an NFA according to the prenex.
        """
        tree = create_tree(_string_split(string))
        return NFA(tree)

    def add_char_in_alphabet(self, char: str):
        """
        Add a character to the alphabet.
        @param char: The character to be added.
        """
        if char in self.alphabet:
            return
        self.alphabet.append(char)

    def _update_links(self, start_state: NodeGraph, final_state: NodeGraph, node_tree):
        graph = self.NFA_Graph(node_tree)
        graph.is_start_state = False
        graph.final_state.is_final_state = False
        start_state.insert_graph(graph, "eps")
        graph.final_state.insert_graph(final_state, "eps")
        graph.update_final_state(final_state)
        graph.update_start_state(start_state)
        return graph

    def NFA_Graph(self, node_tree: NodeTree) -> Optional[NodeGraph]:
        """
        @param node_tree: Tree.
        @return: The initial state of the graph.
        """
        if node_tree.data is None:
            return None
        elif node_tree.data == "void":
            return NodeGraph(-1, False, False)
        elif node_tree.data == "eps":
            self.state_number += 2
            aux = NodeGraph(self.state_number - 2, True, False)
            tmp = NodeGraph(self.state_number - 1, False, True)

            self.states.add(aux)
            self.states.add(tmp)

            aux.insert_graph(tmp, "eps")
            aux.final_state = tmp
            return aux
        elif node_tree.data == "CONCAT":
            left_graph = self.NFA_Graph(node_tree.left)
            left_graph.is_start_state = False

            right_graph = self.NFA_Graph(node_tree.right)
            right_graph.final_state.is_final_state = False
            right_graph.final_state.insert_graph(left_graph, "eps")
            right_graph.update_final_state(left_graph)
            return right_graph
        elif node_tree.data == "UNION":
            q = NodeGraph(self.state_number, True, False)
            f = NodeGraph(self.state_number + 1, False, True)

            self.states.add(q)
            self.states.add(f)
            q.update_final_state(f)

            self.state_number += 2
            self._update_links(q, f, node_tree.right)
            self._update_links(q, f, node_tree.left)
            return q
        elif node_tree.data == "STAR":
            q = NodeGraph(self.state_number, True, False)
            f = NodeGraph(self.state_number + 1, False, True)

            self.states.add(q)
            self.states.add(f)

            self.state_number += 2
            q.update_final_state(f)
            q.insert_graph(f, "eps")

            right_graph = self._update_links(q, f, node_tree.right)
            right_graph.final_state.insert_graph(right_graph, "eps")
            return q
        elif node_tree.data == "PLUS":
            return self.NFA_Graph(NodeTree("CONCAT", node_tree.right, NodeTree("STAR", node_tree.right, None)))
        elif node_tree.data == "MAYBE":
            return self.NFA_Graph(NodeTree("UNION", node_tree.right, NodeTree("eps", None, None)))
        else:
            self.state_number += 2
            left_graph = NodeGraph(self.state_number - 2, True, False)
            right_graph = NodeGraph(self.state_number - 1, False, True)

            self.states.add(left_graph)
            self.states.add(right_graph)

            left_graph.insert_graph(right_graph, node_tree.data)
            left_graph.update_final_state(right_graph)
            self.add_char_in_alphabet(node_tree.data)
            return left_graph


def create_tree(stack: list) -> NodeTree:
    """
    @param stack: List of operators.
    @return: Tree with all operators.
    """
    aux = stack.pop()
    if (aux == "UNION") or (aux == "CONCAT"):
        node = NodeTree(aux, create_tree(stack), create_tree(stack))
        return node
    if aux == "STAR":
        node = NodeTree(aux, create_tree(stack), None)
        return node
    if aux == "PLUS":
        node_aux = create_tree(stack)
        node = NodeTree("CONCAT",  node_aux, NodeTree("STAR", node_aux, None))
        return node
    if aux == "MAYBE":
        node = NodeTree("UNION", NodeTree("eps", None, None), create_tree(stack))
        return node
    return NodeTree(aux, None, None)


def reverse_string(x):
    """
    @param x: The string to be reversed.
    @return: Returns the reversed string.
    """
    return x[::-1]


def _string_split(string: str) -> list:
    """

    @param string: Prenex.
    @return: Transform from a prenext string into a list of operators.
    """
    stack = []
    i = len(string) - 1
    aux = ""
    if i == 0:
        stack.append(string)
        return stack
    while i >= 0:
        if string[i] == "'":
            stack.append(string[i-1])
            i -= 4
            continue
        if string[i] == " ":
            i -= 1
            stack.append(reverse_string(aux))
            aux = ""
            continue
        aux += string[i]
        i -= 1
        if (i == 0) and (aux != ""):
            aux += string[i]
            stack.append(reverse_string(aux))

    return stack

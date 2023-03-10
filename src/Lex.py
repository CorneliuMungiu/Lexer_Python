from __future__ import annotations
from src.NFA import NFA
from src.DFA import DFA
from src.Parser import Parser

from typing import Tuple, List, Dict

def _gel_line(position, word):
    j = 0
    for i in range(position):
        if word[i].endswith("\n"):
            j += 1

    return j

def error_lexer(position, word):
    j = _gel_line(position, word)
    if position == len(word):
        return "No viable alternative at character EOF, line " + str(len(word) - 1)
    else:
        return "No viable alternative at character " + str(position) + ", line " + str(j)



class Lexer:

    """
        This constructor initializes the lexer with a configuration
        The configuration is passed as a dictionary TOKEN -> REGEX

        You are encouraged to use the functions from the past stages to parse the regexes
    """

    def __init__(self, configurations: Dict[str, str]) -> None:
        nfas = []

        for i, lex in enumerate(configurations):
            nfa = NFA.fromPrenex(Parser.toPrenex(configurations[lex]))
            nfa.graph.final_state.lex = lex
            nfa.graph.final_state.lex_rank = i
            nfas.append(nfa)

        main_nfa = nfas[0]

        for nfa in nfas[1:]:
            nfa.graph.is_start_state = False
            main_nfa.graph.insert_graph(nfa.graph, "eps")
            main_nfa.alphabet.extend(set(nfa.alphabet) - set(main_nfa.alphabet))
            main_nfa.states.update(nfa.states)

        self.dfa = DFA.fromNFA(main_nfa)

    """
        The main functionality of the lexer, receives a word and lexes it
        according to the provided configuration.

        The return value is either a List of tuples (TOKEN, LEXEM) if the lexer succedes
        or a string message if the lexer fails
    """

    def lex(self, word: str) -> List[Tuple[str, str]] | str:
        final_list = []
        state = self.dfa.graph
        string = str()
        previous_string = str()
        previous_token = str()
        counter = -1
        previous_i = -1
        while True:
            counter += 1
            if counter == len(word):
                if previous_i == counter - 1:
                    break
                if not (len(previous_string) == 0):
                    string = str()
                    final_list.append((previous_token, previous_string))
                    state = self.dfa.graph
                    counter = previous_i + 1
                else:
                    return "No viable alternative at character EOF, line " + str(_gel_line(len(word) - 1, word))


            state = self.dfa.xNextx(state, word[counter])

            string += word[counter]
            if not (len(state.lex) == 0):
                previous_i = counter
                previous_string = str(string)
                previous_token = state.lex
            elif len(previous_string) != 0 and len(previous_token) != 0:
                if state == self.dfa.sink:
                    string = str()
                    counter = previous_i
                    final_list.append((previous_token, previous_string))
                    previous_string = str()
                    state = self.dfa.graph
            else:
                if state == self.dfa.sink:
                    return error_lexer(counter, word)



        if len(previous_string) != 0 or len(previous_token) != 0:
            final_list.append((previous_token, previous_string))
        elif previous_i == 0:
            return error_lexer(counter, word)

        return final_list
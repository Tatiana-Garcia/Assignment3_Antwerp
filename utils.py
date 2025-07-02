from typing import *
import aalpy

Symbol = str
Word = List[Symbol]

empty_word = []


def concat(w1: Word, w2: Word) -> Word:
    if w1 is empty_word:
        return w2
    if w2 is empty_word:
        return w1
    return w1 + w2


def append_symbol(w: Word, s: Symbol) -> Word:
    return w + [s]


def prepend_symbol(s: Symbol, w: Word) -> Word:
    return [s] + w


def prefixes(w: Word) -> List[Word]:
    return [w[:i] for i in range(1, len(w) + 1)]


def suffixes(w: Word) -> List[Word]:
    return [w[-i:] for i in range(1, len(w) + 1)]


def run_experiment(tableType, lstar, num_states: int, alphabet_size: int) -> Tuple[int, int, int, int]:
    class CounterEqOracle(aalpy.RandomWalkEqOracle):
        def __init__(self, alphabet: list, sul: aalpy.SUL):
            super().__init__(alphabet, sul)
            self.counter = 0

        @override
        def find_cex(self, hypothesis):
            self.counter += 1
            return super().find_cex(hypothesis)

    class TableWithSizes(tableType):
        n_representatives = 0
        n_suffixes = 0

        @override
        def construct_hypothesis(self):
            TableWithSizes.n_representatives = len(self.get_representatives())
            TableWithSizes.n_suffixes = len(self.separators)
            return super().construct_hypothesis()

    automaton = aalpy.generate_random_deterministic_automata(
        automaton_type="dfa", num_states=num_states, input_alphabet_size=alphabet_size)
    sul = aalpy.AutomatonSUL(automaton)
    alphabet = automaton.get_input_alphabet()
    eq_oracle = CounterEqOracle(alphabet, sul)
    lstar(sul, alphabet, eq_oracle, TableWithSizes)
    return (sul.num_queries, eq_oracle.counter, TableWithSizes.n_representatives, TableWithSizes.n_suffixes)

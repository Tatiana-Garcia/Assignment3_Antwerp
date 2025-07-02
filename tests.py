from aalpy.utils import bisimilar
import aalpy
import unittest
from utils import *


def run_tests_observation_table(tableType):
    class TestLoader(unittest.TestLoader):
        def loadTestsFromTestCase(self, testCaseClass):
            testCaseNames = self.getTestCaseNames(testCaseClass)
            return self.suiteClass([testCaseClass(testCase, tableType) for testCase in testCaseNames])

    suite = TestLoader().loadTestsFromTestCase(TestObservationTable)
    runner = unittest.TextTestRunner()
    assert (len(runner.run(suite).failures) == 0)


def run_tests_lstar(tableType, lstar):
    class TestLoader(unittest.TestLoader):
        def loadTestsFromTestCase(self, testCaseClass):
            testCaseNames = self.getTestCaseNames(testCaseClass)
            return self.suiteClass([testCaseClass(testCase, tableType, lstar) for testCase in testCaseNames])

    suite = TestLoader().loadTestsFromTestCase(TestLStar)
    runner = unittest.TextTestRunner()
    assert (len(runner.run(suite).failures) == 0)


class TestObservationTable(unittest.TestCase):
    def __init__(self, methodName, tableType):
        super().__init__(methodName)
        self.tableType = tableType

    def setUp(self):
        self.automaton = aalpy.Dfa.from_state_setup(
            {
                "q0": (False, {"a": "q1", "b": "q2"}),
                "q1": (False, {"a": "q0", "b": "q3"}),
                "q2": (True, {"a": "q3", "b": "q0"}),
                "q3": (False, {"a": "q2", "b": "q1"}),
            }
        )
        self.sul = aalpy.AutomatonSUL(self.automaton)
        self.alphabet = ["a", "b"]

    def test_initialization(self):
        table = self.tableType(self.sul, self.alphabet)
        self.assertEqual(len(table.separators), 1)
        self.assertEqual(table.separators, [empty_word])
        self.assertEqual(len(table.rows), 3)
        self.assertEqual(sorted(table.get_representatives()),
                         sorted([empty_word]))
        self.assertEqual(table.get_row(empty_word).content, [False])
        self.assertEqual(table.number_rows(), 3)
        self.assertIsNotNone(table.get_row(["a"]))
        self.assertIsNotNone(table.get_row(["b"]))
        self.assertEqual(table.get_row(["a"]).content, [False])
        self.assertEqual(table.get_row(["b"]).content, [True])

    def test_add_representative(self):
        table = self.tableType(self.sul, self.alphabet)
        table.add_representative(["a"])
        self.assertEqual(table.separators, [empty_word])
        self.assertEqual(
            sorted(table.get_representatives()), sorted([empty_word, ["a"]])
        )
        self.assertEqual(table.number_rows(), 5)
        self.assertIsNotNone(table.get_row(["a"]))
        self.assertIsNotNone(table.get_row(["a", "a"]))
        self.assertIsNotNone(table.get_row(["a", "b"]))
        self.assertIsNotNone(table.get_row(["b"]))
        self.assertEqual(table.get_row(empty_word).content, [False])
        self.assertEqual(table.get_row(["a"]).content, [False])
        self.assertEqual(table.get_row(["b"]).content, [True])
        self.assertEqual(table.get_row(["a", "a"]).content, [False])
        self.assertEqual(table.get_row(["a", "b"]).content, [False])
        table.add_representative(["a"])
        self.assertEqual(table.separators, [empty_word])
        self.assertEqual(
            sorted(table.get_representatives()), sorted([empty_word, ["a"]])
        )
        self.assertEqual(table.number_rows(), 5)
        self.assertIsNotNone(table.get_row(["a"]))
        self.assertIsNotNone(table.get_row(["a", "a"]))
        self.assertIsNotNone(table.get_row(["a", "b"]))
        self.assertIsNotNone(table.get_row(["b"]))
        self.assertEqual(table.get_row(empty_word).content, [False])
        self.assertEqual(table.get_row(["a"]).content, [False])
        self.assertEqual(table.get_row(["b"]).content, [True])
        self.assertEqual(table.get_row(["a", "a"]).content, [False])
        self.assertEqual(table.get_row(["a", "b"]).content, [False])

    def test_add_separator(self):
        table = self.tableType(self.sul, self.alphabet)
        table.add_representative(["a"])
        table.add_separator(["b"])
        self.assertEqual(sorted(table.separators), sorted([empty_word, ["b"]]))
        self.assertEqual(table.number_rows(), 5)
        self.assertIsNotNone(table.get_row(["a"]))
        self.assertIsNotNone(table.get_row(["a", "a"]))
        self.assertIsNotNone(table.get_row(["a", "b"]))
        self.assertIsNotNone(table.get_row(["b"]))
        self.assertEqual(table.get_row(empty_word).content, [False, True])
        self.assertEqual(table.get_row(["a"]).content, [False, False])
        self.assertEqual(table.get_row(["b"]).content, [True, False])
        self.assertEqual(table.get_row(["a", "a"]).content, [False, True])
        self.assertEqual(table.get_row(["a", "b"]).content, [False, False])

    def test_make_closed(self):
        table = self.tableType(self.sul, self.alphabet)
        unclosed = table.find_unclosed()
        self.assertIsNotNone(unclosed)
        self.assertEqual(unclosed.word, ["b"])
        table.make_closed(unclosed)
        self.assertEqual(table.number_rows(), 5)
        self.assertIsNotNone(table.get_row(["a"]))
        self.assertIsNotNone(table.get_row(["b"]))
        self.assertIsNotNone(table.get_row(["b", "a"]))
        self.assertIsNotNone(table.get_row(["b", "b"]))
        self.assertEqual(table.get_row(empty_word).content, [False])
        self.assertEqual(table.get_row(["a"]).content, [False])
        self.assertEqual(table.get_row(["b"]).content, [True])
        self.assertEqual(table.get_row(["b", "a"]).content, [False])
        self.assertEqual(table.get_row(["b", "b"]).content, [False])
        self.assertIsNone(table.find_unclosed())

    def test_make_consistent(self):
        table = self.tableType(self.sul, self.alphabet)
        table.add_representative(["a"])
        inconsistency = table.find_inconsistency()
        self.assertIsNotNone(inconsistency)
        self.assertIn(inconsistency[0].word, [["b"], ["a", "b"]])
        self.assertIn(inconsistency[1].word, [["b"], ["a", "b"]])
        self.assertNotEqual(inconsistency[0].word, inconsistency[1].word)
        self.assertEqual(inconsistency[2], "b")
        table.make_consistent(
            inconsistency[0], inconsistency[1], inconsistency[2])
        self.assertIsNone(table.find_inconsistency())

        table = self.tableType(self.sul, self.alphabet)
        table.add_representative(["b"])
        table.add_representative(["a"])
        table.add_representative(["a", "b"])
        table.add_separator(["b"])
        inconsistency = table.find_inconsistency()
        self.assertIsNotNone(inconsistency)

    def test_hypothesis(self):
        table = self.tableType(self.sul, self.alphabet)
        table.make_closed_and_consistent()
        hypothesis = table.construct_hypothesis()
        self.assertEqual(hypothesis.size, 2)
        target = aalpy.Dfa.from_state_setup(
            {
                "epsilon": (False, {"a": "epsilon", "b": "b"}),
                "b": (True, {"a": "epsilon", "b": "epsilon"}),
            }
        )
        self.assertTrue(bisimilar(hypothesis, target))

        table.add_representative(["a"])
        table.add_representative(["a", "b"])
        table.add_separator(["b"])
        table.add_separator(["a", "b"])
        table.make_closed_and_consistent()
        hypothesis = table.construct_hypothesis()
        self.assertEqual(hypothesis.size, 4)
        target = aalpy.Dfa.from_state_setup(
            {
                "epsilon": (False, {"a": "a", "b": "b"}),
                "a": (False, {"a": "epsilon", "b": "ab"}),
                "b": (True, {"a": "ab", "b": "epsilon"}),
                "ab": (False, {"a": "b", "b": "a"}),
            }
        )
        self.assertTrue(bisimilar(hypothesis, target))

    def test_counterexample(self):
        table = self.tableType(self.sul, self.alphabet)
        table.make_closed_and_consistent()
        self.assertEqual(table.number_rows(), 5)
        self.assertEqual(table.number_separators(), 1)
        self.assertFalse(
            bisimilar(table.construct_hypothesis(), self.automaton))
        table.process_counterexample(["a", "b"])
        self.assertEqual(table.number_rows(), 9)
        self.assertEqual(table.number_separators(), 1)
        table.make_closed_and_consistent()
        self.assertEqual(table.number_rows(), 9)
        self.assertEqual(table.number_separators(), 3)
        self.assertTrue(
            bisimilar(table.construct_hypothesis(), self.automaton))


class TestLStar(unittest.TestCase):
    def __init__(self, methodName, tableType, lstar):
        super().__init__(methodName)
        self.tableType = tableType
        self.lstar = lstar

    def test_lstar_fixed_dfa(self):
        automaton = aalpy.Dfa.from_state_setup(
            {
                "q0": (False, {"a": "q1", "b": "q2"}),
                "q1": (False, {"a": "q0", "b": "q3"}),
                "q2": (True, {"a": "q3", "b": "q0"}),
                "q3": (False, {"a": "q2", "b": "q1"}),
            }
        )
        sul = aalpy.AutomatonSUL(automaton)
        alphabet = ["a", "b"]
        eq_oracle = aalpy.PerfectKnowledgeEqOracle(alphabet, sul, automaton)
        result = self.lstar(sul, alphabet, eq_oracle, self.tableType)

        eq_oracle = aalpy.RandomWalkEqOracle(alphabet, sul)
        result = self.lstar(sul, alphabet, eq_oracle, self.tableType)

    def test_lstar_random(self):
        automaton = aalpy.generate_random_deterministic_automata(
            automaton_type="dfa", num_states=6, input_alphabet_size=3
        )
        sul = aalpy.AutomatonSUL(automaton)
        alphabet = automaton.get_input_alphabet()
        eq_oracle = aalpy.PerfectKnowledgeEqOracle(alphabet, sul, automaton)
        result = self.lstar(sul, alphabet, eq_oracle, self.tableType)

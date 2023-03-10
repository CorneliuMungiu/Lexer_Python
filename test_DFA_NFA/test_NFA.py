import unittest
from src.NFA import NFA


class NFATests(unittest.TestCase):
	def test_nfa_from_eps(self):
		self.assertTrue(NFA.fromPrenex("eps").accepts(""))


	def test_nfa_from_space(self):
		self.assertTrue(NFA.fromPrenex("' '").accepts(" "))
		self.assertFalse(NFA.fromPrenex("' '").accepts(""))


	def test_nfa_from_void(self):
		self.assertFalse(NFA.fromPrenex("void").accepts(""))


	def test_nfa_from_char(self):
		self.assertTrue(NFA.fromPrenex("a").accepts("a"))
		self.assertFalse(NFA.fromPrenex("a").accepts("b"))


	def test_nfa_from_complex_expression1(self):
		expr = "CONCAT a b"
		self.assertTrue(NFA.fromPrenex(expr).accepts("ab"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("aba"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("ba"))


	def test_nfa_from_complex_expression2(self):
		expr = "UNION a b"
		self.assertTrue(NFA.fromPrenex(expr).accepts("a"))
		self.assertTrue(NFA.fromPrenex(expr).accepts("b"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("ab"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("ba"))


	def test_nfa_from_star1(self):
		expr = "STAR a"
		self.assertTrue(NFA.fromPrenex(expr).accepts(""))
		self.assertTrue(NFA.fromPrenex(expr).accepts("a"))
		self.assertTrue(NFA.fromPrenex(expr).accepts("aaaaaaaaaaa"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("aaaaabaaaaa"))


	def test_nfa_from_complex_expression3(self):
		expr = "STAR UNION a b"
		self.assertTrue(NFA.fromPrenex(expr).accepts("aaababaaabaaaaa"))
		self.assertTrue(NFA.fromPrenex(expr).accepts("aaaaaaaaaa"))
		self.assertTrue(NFA.fromPrenex(expr).accepts("bbbbbbbbbbb"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("baaabbbabaacabbbaaabbb"))


	def test_nfa_from_complex_expression4(self):
		expr = "STAR CONCAT a b"
		self.assertTrue(NFA.fromPrenex(expr).accepts("ababababab"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("abababababa"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("abababaabab"))


	def test_nfa_from_complex_expression5(self):
		expr = "STAR CONCAT a b"
		self.assertTrue(NFA.fromPrenex(expr).accepts("ababababab"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("abababababa"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("abababaabab"))


	def test_nfa_from_complex_expression6(self):
		expr = "CONCAT UNION b STAR a STAR c"
		self.assertTrue(NFA.fromPrenex(expr).accepts("aaaaaaaaaccccc"))
		self.assertTrue(NFA.fromPrenex(expr).accepts("bccccccccc"))
		self.assertFalse(NFA.fromPrenex(expr).accepts("bbbbccccccccc"))


	def test_nfa_from_complex_expression7(self):
		expr = "CONCAT a STAR a"
		self.assertTrue(NFA.fromPrenex(expr).accepts("aaa"))
		self.assertFalse(NFA.fromPrenex(expr).accepts(""))
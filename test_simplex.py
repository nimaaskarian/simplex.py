from fractions import Fraction
import unittest
from simplex import read_expression, simplex_data, solve_simplex_and_print_tables

class TestReadExpression(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(read_expression("x - 10y"), (["x", "y"], [Fraction(1), Fraction(-10)]))

    def test_complex_name(self):
        self.assertEqual(read_expression("-nima(haha) - 10 matty(?)"), (["matty(?)", "nima(haha)"], [Fraction(-10), Fraction(-1)]))

    def test_fraction_coefficient(self):
        self.assertEqual(read_expression("-1/2x1 + 10/69x2"), (["x1", "x2"], [Fraction(-1, 2), Fraction(10, 69)]))

    def test_coefficient_multiply(self):
        self.assertEqual(read_expression("-1/2 2 x1 + 10/69 3 x2"), (["x1", "x2"], [Fraction(-1, 1), Fraction(10, 23)]))

class TestSimplexData(unittest.TestCase):
    def test_min(self):
        self.assertEqual(simplex_data("""min 4x-5y 
3x + 2y <= 6
-x + y <= 1
x+2y <= 5"""),("min", "z", (["x", "y", "s1", "s2","s3"], [Fraction(4),Fraction(-5), Fraction(0), Fraction(0), Fraction(0)]), [
                     ((["x", "y", "s1", "s2","s3"], [Fraction(3),Fraction(2), Fraction(1), Fraction(0), Fraction(0)]), Fraction(6),"<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(-1),Fraction(1), Fraction(0), Fraction(1), Fraction(0)]), Fraction(1),"<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(1),Fraction(2), Fraction(0), Fraction(0), Fraction(1)]), Fraction(5),"<="),
                         ] ))

    def test_comment_and_empty_line(self):
        self.assertEqual(simplex_data("""min 4x-5y 
3x + 2y <= 6
# this is a very long comment.

   
	   
-x + y <= 1
  # 4x + 10y <= 1
x+2y <= 5"""),("min", "z", (["x", "y", "s1", "s2","s3"], [Fraction(4),Fraction(-5), Fraction(0), Fraction(0), Fraction(0)]), [
                     ((["x", "y", "s1", "s2","s3"], [Fraction(3),Fraction(2), Fraction(1), Fraction(0), Fraction(0)]), Fraction(6),"<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(-1),Fraction(1), Fraction(0), Fraction(1), Fraction(0)]), Fraction(1),"<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(1),Fraction(2), Fraction(0), Fraction(0), Fraction(1)]), Fraction(5),"<="),
                         ] ))

    def test_not_defined_variable_constraints(self):
        self.assertEqual(simplex_data("""min 4x-5y 
2y <= 6
-x <= 1
x+2y <= 5"""),("min", "z", (["x", "y", "s1", "s2","s3"], [Fraction(4),Fraction(-5), Fraction(0), Fraction(0), Fraction(0)]), [
                     ((["x", "y", "s1", "s2","s3"], [Fraction(0),Fraction(2), Fraction(1), Fraction(0), Fraction(0)]), Fraction(6), "<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(-1),Fraction(0), Fraction(0), Fraction(1), Fraction(0)]), Fraction(1), "<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(1),Fraction(2), Fraction(0), Fraction(0), Fraction(1)]), Fraction(5), "<="),
                         ] ))

    def test_max(self):
        self.assertEqual(simplex_data("""max 4x-5y 
3x + 2y <= 6
-x + y <= 1
x+2y <= 5"""),("max", "z", (["x", "y", "s1", "s2","s3"], [Fraction(4),Fraction(-5), Fraction(0), Fraction(0), Fraction(0)]), [
                     ((["x", "y", "s1", "s2","s3"], [Fraction(3),Fraction(2), Fraction(1), Fraction(0), Fraction(0)]), Fraction(6), "<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(-1),Fraction(1), Fraction(0), Fraction(1), Fraction(0)]), Fraction(1), "<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(1),Fraction(2), Fraction(0), Fraction(0), Fraction(1)]), Fraction(5), "<="),
                         ] ))
    def test_wrong_kind(self):
        self.assertRaises(Exception,simplex_data, """nima 4x-5y 
3x + 2y <= 6
-x + y <= 1
x+2y <= 5""")

class TestSolveSimplex(unittest.TestCase):
    def test_min_solvable(self):
        from collections import namedtuple
        Args = namedtuple('Args', ['table_only', 'tablefmt', 'html'])
        args = Args(table_only=False, tablefmt="simple_outline", html=False)
        self.assertEqual(Fraction(-29, 5), solve_simplex_and_print_tables(("min", "z", (["x", "y", "s1", "s2","s3"], [Fraction(4),Fraction(-5), Fraction(0), Fraction(0), Fraction(0)]), [
                     ((["x", "y", "s1", "s2","s3"], [Fraction(3),Fraction(2), Fraction(1), Fraction(0), Fraction(0)]), Fraction(6), "<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(-1),Fraction(1), Fraction(0), Fraction(1), Fraction(0)]), Fraction(1), "<="),
                     ((["x", "y", "s1", "s2","s3"], [Fraction(1),Fraction(2), Fraction(0), Fraction(0), Fraction(1)]), Fraction(5), "<="),
                         ] ), args))

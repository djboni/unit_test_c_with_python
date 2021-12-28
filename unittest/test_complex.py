#!/usr/bin/python3
import unittest
from load import load

module, ffi = load("complex.c", module_name="complex_")


class ComplexTest(unittest.TestCase):
    def test_addition(self):
        result = module.add_complex([0, 1], [2, 3])
        self.assertEqual(result.real, 2)
        self.assertEqual(result.imaginary, 4)


if __name__ == "__main__":
    unittest.main()

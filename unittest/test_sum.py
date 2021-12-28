#!/usr/bin/python3
import unittest
from load import load

module, ffi = load("sum.c", module_name="sum_")


class SumTest(unittest.TestCase):
    def setUp(self):
        module.sum_reset()

    def test_zero(self):
        self.assertEqual(module.sum(0), 0)

    def test_one(self):
        self.assertEqual(module.sum(1), 1)

    def test_multiple(self):
        self.assertEqual(module.sum(2), 2)
        self.assertEqual(module.sum(4), 2 + 4)


if __name__ == "__main__":
    unittest.main()

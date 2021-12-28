#!/usr/bin/python3
from load_c import load
import unittest

module, ffi = load("add.c")


class AddTest(unittest.TestCase):
    def test_addition(self):
        # Function name 'add' from created module
        self.assertEqual(module.add(1, 2), 1 + 2)


if __name__ == "__main__":
    unittest.main()

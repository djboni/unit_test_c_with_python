#!/usr/bin/python3
import unittest
from load import load

module, ffi = load("add.c", module_name="add_")


class AddTest(unittest.TestCase):
    def test_addition(self):
        # Function name 'add' from created module
        self.assertEqual(module.add(1, 2), 1 + 2)


if __name__ == "__main__":
    unittest.main()

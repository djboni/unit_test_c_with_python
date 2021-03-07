#!/usr/bin/python3
from load_c import load
import unittest

class AddTest(unittest.TestCase):
  def setUp(self):
    # File name 'add' for add.c and add.h
    # Compiles python module with this files
    self.module, self.ffi = load('add')
    
  def test_addition(self):
    # Function name 'add' from created module
    self.assertEqual(self.module.add(1, 2), 1 + 2)

if __name__ == '__main__':
    unittest.main()


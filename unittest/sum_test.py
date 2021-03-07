#!/usr/bin/python3
from load_c import load
import unittest

class SumTest(unittest.TestCase):
  def setUp(self):
    self.module, self.ffi = load('sum')
  
  def test_zero(self):
    self.assertEqual(self.module.sum(0), 0)
  
  def test_one(self):
    self.assertEqual(self.module.sum(1), 1)
  
  def test_multiple(self):
    self.assertEqual(self.module.sum(2), 2)
    self.assertEqual(self.module.sum(4), 2 + 4)

if __name__ == '__main__':
    unittest.main()


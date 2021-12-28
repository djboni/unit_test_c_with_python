#!/usr/bin/python3
import unittest
import unittest.mock
from load import load

module_name = "pysim_"

source_files = ["add.c", "complex.c", "gpio.c", "main.c"]

include_paths = [
    ".",
    "./includes",
]

compiler_options = [
    "-std=c90",
    "-pedantic",
]

module, ffi = load(
    source_files, include_paths, compiler_options, module_name=module_name
)


class AddTest(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(module.add(1, 2), 1 + 2)


class ComplexTest(unittest.TestCase):
    def test_addition(self):
        result = module.complex_add([0, 1], [2, 3])
        self.assertEqual(result.real, 2)
        self.assertEqual(result.imaginary, 4)


class GPIOTest(unittest.TestCase):
    def test_read_gpio0(self):
        @ffi.def_extern()
        def read_gpio0():
            return 42

        self.assertEqual(module.read_gpio(0), 42)

    def test_read_gpio1(self):
        read_gpio1 = unittest.mock.MagicMock(return_value=21)
        ffi.def_extern("read_gpio1")(read_gpio1)
        self.assertEqual(module.read_gpio(1), 21)
        read_gpio1.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()

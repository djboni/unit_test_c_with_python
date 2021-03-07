# Unit-Test C with Python

This repository shows examples of how to unit-test C source code using the Python language.

# Unit testing

The examples are from Alexander Steffen's presentation [Writing unit tests for C code in Python](https://www.youtube.com/watch?v=zW_HyDTPjO0) in EuroPython Conference (21 July 2016).

The examples given by Alexander Steffen were:

* add (add_test.py, add.c, add.h)
* sum (sum_test.py, sum.c, sum.h)
* complex (complex_test.py, complex.c, complex.h, types.h)
* gpio (gpio_test.py, gpio.c, gpio.h, gpio_lib.h)

They show how to test a function (add), how to deal with global variables (sum), how to deal with multiple include files (complex), and how to mock or mimic unavailable external functions (gpio).

The function `load()` from `load_c.py` does all the work of creating and importing the C source code as a library that can be tested with Python's `unittest` module.

## Quick example

```c
/* add.h */

int add(int a, int b);
```

```c
/* add.c */

#include "add.h"

int add(int a, int b)
{
  return a + b;
}
```

```python
# add_test.py

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
```

# Integration testing

Alexander Steffen's presentation [Testing microcontroller firmware with Python](https://www.youtube.com/watch?v=-SvmjCWBX10) in EuroPython Conference (10 July 2017).

To be able to unit-test your C code with Python, the C code must be modulare with respect to the hardware interface.

```
+-----------+            +------------+
|Application|      \     |Application |
|-----------|   +---\    |------------|
|    HAL    |   |    )   |   Python   |
|-----------|   +---/    |------------|
| Hardware  |      /     |Code Network|
+-----------+            +------------+
```

Python functions and constructs will take HAL's place, providing similar functionality or even made out values to be processed by the functions under test.

Application source code and the headers of HAL (Hardware Abstraction Layer) are processed with CFFI, compiled with GCC and loaded into Python.

```
                \
application/*.c |
                |o => CFFI => GCC => Python 
hal/*.h         |
                /
```

With the C source code imported as a module, you can use Python's `unittest` module to write tests for the C functions.

# More resources on testing C code

* Alexander Steffen [Writing unit tests for C code in Python](https://www.youtube.com/watch?v=zW_HyDTPjO0)
* Alexander Steffen [Testing microcontroller firmware with Python](https://www.youtube.com/watch?v=-SvmjCWBX10)
* Benno Rice [You Can't Unit Test C, Right?](https://www.youtube.com/watch?v=z-uWt5wVVkU) (How to test C with C)

# Frameworks for unit-tests

* [cmocka](https://cmocka.org/)
* [Check](https://libcheck.github.io/check/)
* [ATF](https://github.com/jmmv/atf) and [Kyua](https://github.com/jmmv/kyua/)
* [Acutest](https://github.com/mity/acutest)
* [C++ Boost.Test](https://www.boost.org/doc/libs/1_75_0/libs/test/doc/html/index.html)
* [Python unittest](https://docs.python.org/3/library/unittest.html)

# Code coverage tools

* [Gcov](https://gcc.gnu.org/onlinedocs/gcc/Gcov.html)
* [gcovr](https://gcovr.com/en/stable/)
* [lcov](https://github.com/linux-test-project/lcov) and genhtml

# TODO

* Integration testing: Example code
* Is there a way to use include Gcov to test statement or branch coverage when testing C code with Python?


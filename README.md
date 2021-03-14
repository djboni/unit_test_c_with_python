# Unit-Test C with Python

This project allows you to import normal C source code into a Python as a module.

The function `load()`, defined in `load_c.py`, does all the work of creating the module from the source code.

The source code and the headers used within them are processed with CFFI, compiled with GCC, and loaded as a Python module.

```
             \
source/*.c   |
             |o => CFFI => GCC => Python 
includes/*.h |
             /
```

With that you can do lots of cool things with, such as:

* Create unit-tests of single C source file.
* Create integration-test of multiple C source files.
* Test embedded C code

## Quick example

Testing an add function.

```c
/* File: add.h */

int add(int a, int b);
```

```c
/* File: add.c */

#include "add.h"

int add(int a, int b)
{
  return a + b;
}
```

```python
# File: test_add.py

from load_c import load
import unittest

module, ffi = load('add.c')

class AddTest(unittest.TestCase):

  def testAddtion(self):
    self.assertEqual(module.add(1, 2), 1 + 2)

if __name__ == '__main__':
  unittest.main()
```

## Another example

Testing a semaphore implementation.

```python
# File: test_semaphore.py

from load_c import load
import unittest

source_files = [
  'semaphore.c',
  'other_file.c',
]

include_paths = [
  '.',
  './includes',
]

compiler_options = [
  '-std=c90',
  '-pedantic',
]

module, ffi = load(source_files, include_paths, compiler_options)

class SemaphoreInit(unittest.TestCase):

  def setUp(self):
    self.psem = ffi.new("struct Semaphore_t[1]")
    self.sem = self.psem[0]

  def testInitBinary(self):
    count, max_ = 1, 1
    module.Semaphore_init(self.psem, count, max_)
    # Count and Max OK
    self.assertEqual(self.sem.Count, count)
    self.assertEqual(self.sem.Max, max_)

  def testInitCounter(self):
    count, max_ = 3, 5
    module.Semaphore_init(self.psem, count, max_)
    # Count and Max OK
    self.assertEqual(self.sem.Count, count)
    self.assertEqual(self.sem.Max, max_)

if __name__ == '__main__':
  unittest.main()
```

## Testing embedded C code

To be able to test your embedded C code with Python (unit-test or integration test), the C code must be modular with respect to the hardware interface (or HAL - Hardware Abstraction Layer).

Python functions and constructs will take HAL's place, providing similar functionality or even made out values to be processed by the functions under test.

```
+-----------+            +-----------+
|Application|      \     |Application|
|-----------|   +---\    |-----------|
|    HAL    |   |    )   |  Python   |
|-----------|   +---/    |-----------|
| Hardware  |      /     | Simulated |
+-----------+            |peripherals|
                         +-----------+
```

## Example of mocking hardware dependent calls

Here is an example: the library exposed on gpio_lib.h has no source code available. We test if `read_gpio(int)` uses the correct calls to `read_gpio0()` and `read_gpio1()` using mock functions.

```c
/* File: gpio_lib.h */

int read_gpio0(void);
int read_gpio1(void);
```

```c
/* File: gpio.h */

int read_gpio(int number);
```

```c
/* File: gpio.c */

#include "gpio.h"
#include "gpio_lib.h"

int read_gpio(int number)
{
  switch(number)
  {
    case 0:
      return read_gpio0();
    case 1:
      return read_gpio1();
    default:
      return -1;
  }
}
```

```python
# File: test_gpio.py

from load_c import load
import unittest, unittest.mock

source_files = [
  'gpio.c',
]

include_paths = [
  '.',
  './includes',
]

compiler_options = [
  '-std=c90',
  '-pedantic',
]

module, ffi = load(source_files, include_paths, compiler_options)

class GPIOTest(unittest.TestCase):

  def test_read_gpio0(self):

    # Define read_gpio0() returning 42
    @ffi.def_extern()
    def read_gpio0():
      return 42

    self.assertEqual(module.read_gpio(0), 42)
  
  def test_read_gpio1(self):
  
    # Mock read_gpio1() to return 21
    read_gpio1 = unittest.mock.MagicMock(return_value=21)
    ffi.def_extern('read_gpio1')(read_gpio1)
    
    self.assertEqual(module.read_gpio(1), 21)
    
    # Check if mock was called once with no parameters
    read_gpio1.assert_called_once_with()

if __name__ == '__main__':
  unittest.main()
```

## Troubleshooting errors and problems

If you have some trouble loading your C files into a module, take a look at the file [ERRORS.md](https://github.com/djboni/unit-test-c-with-python/blob/master/ERRORS.md) for known errors.

## References

This is based on Alexander Steffen's presentations:

* Alexander Steffen - [Writing unit tests for C code in Python](https://www.youtube.com/watch?v=zW_HyDTPjO0) - EuroPython Conference (21 July 2016)
* Alexander Steffen - [Testing microcontroller firmware with Python](https://www.youtube.com/watch?v=-SvmjCWBX10) - EuroPython Conference (10 July 2017).

Other useful presentations:

* Benno Rice - [You Can't Unit Test C, Right?](https://www.youtube.com/watch?v=z-uWt5wVVkU) (How to test C with C)

### Frameworks for unit-tests

* [cmocka](https://cmocka.org/)
* [Check](https://libcheck.github.io/check/)
* [ATF](https://github.com/jmmv/atf) and [Kyua](https://github.com/jmmv/kyua/)
* [Acutest](https://github.com/mity/acutest)
* [C++ Boost.Test](https://www.boost.org/doc/libs/1_75_0/libs/test/doc/html/index.html)
* [Python unittest](https://docs.python.org/3/library/unittest.html)

### Code coverage tools

* [Gcov](https://gcc.gnu.org/onlinedocs/gcc/Gcov.html)
* [gcovr](https://gcovr.com/en/stable/)
* [lcov](https://github.com/linux-test-project/lcov) and genhtml

## TODO

* Is there a way to use Gcov to test statement or branch coverage when testing C code with Python?


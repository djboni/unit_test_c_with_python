#include "complex.h"

complex complex_add(complex a, complex b) {
    a.real += b.real;
    a.imaginary += b.imaginary;
    return a;
}

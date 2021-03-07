#include "complex.h"

complex add(complex a, complex b)
{
  a.real += b.real;
  a.imaginary += b.imaginary;
  return a;
}

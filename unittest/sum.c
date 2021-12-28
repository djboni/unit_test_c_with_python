#include "sum.h"

static int _sum = 0;

int sum(int a) {
    _sum += a;
    return _sum;
}

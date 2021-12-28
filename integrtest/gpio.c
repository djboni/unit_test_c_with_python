#include "gpio.h"
#include "gpio_lib.h"

int read_gpio(int number) {
    switch (number) {
    case 0:
        return read_gpio0();
    case 1:
        return read_gpio1();
    default:
        return -1;
    }
}

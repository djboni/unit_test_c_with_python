all: add.o sum.o complex.o gpio.o test

test:
	python3 -m unittest

gpio.o: gpio.c gpio.h gpio_lib.h
	gcc -c -o $@ $<

complex.o: complex.c complex.h types.h
	gcc -c -o $@ $<

%.o: %.c %.h
	gcc -c -o $@ $<

clean:
	rm -fr *.o *.so *_.c *.pyc __pycache__/

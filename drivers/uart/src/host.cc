#include <uart.h>
#include <stdio.h>

bool uart::init(void)
{
	return true;
}

int uart::putchar(int c)
{
	return ::putchar(c);
}

#include <uart.h>
#include <stdio.h>

void uart::init(void)
{
}

int uart::putchar(int c)
{
	return ::putchar(c);
}

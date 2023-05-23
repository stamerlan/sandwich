#include <cstdio>
#include <uart.h>

int main(void)
{
	uart::init();
	printf("Hello world\n");
	return 0;
}

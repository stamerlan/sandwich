#include <cstdio>
#include <uart.h>
#include <sandwich/sched.h>

int main(void)
{
	uart::init();
	sandwich::sched::init();

	return 0;
}

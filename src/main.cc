#include <cstdio>
#include <uart.h>
#include <sched/sched.h>

static bool sched_test(void)
{
	printf("sched_test()\n");
	return true;
}
SANDWICH_TASK(sched_test);

static bool uart_task(void)
{
	printf("uart_task");
	return true;
}
SANDWICH_TASK(uart_task);

int main(void)
{
	uart::init();
	sandwich::sched::init();

	return 0;
}

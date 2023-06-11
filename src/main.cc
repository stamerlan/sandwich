#include <cstdio>
#include <uart.h>
#include <sched/sched.h>

static bool test(void)
{
	printf("task\n");
	return true;
}
SANDWICH_TASK(test);

static bool test2(void)
{
	printf("task2\n");
	return true;
}
SANDWICH_TASK(test2);

int main(void)
{
	uart::init();
	sandwich::sched::init();

	sandwich::sched::wakeup(&sandwich_task_test);
	sandwich::sched::wakeup(&sandwich_task_test2);

	for (int i = 0; i < 8; i++)
		sandwich::sched::run();

	return 0;
}

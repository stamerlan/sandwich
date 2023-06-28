#include <cstdio>
#include <uart.h>
#include <sandwich/sched.h>

static void sched_task(void)
{
	printf("task\n");
}

static void sched_task2(void)
{
	printf("task2\n");
}

int main(void)
{
	uart::init();
	sandwich::sched::init();

	sandwich::sched::task_t task("task", sched_task);
	task.wakeup();

	sandwich::sched::task_t task2("task2", sched_task2);
	task2.wakeup();

	for (int i = 0; i < 8; i++)
		sandwich::sched::run();


	return 0;
}

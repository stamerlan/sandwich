#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <arch/irq.h>
#include <bcm2837_mbox.h>
#include <sandwich/sched.h>
#include <uart.h>

static void sched_task(void)
{
	printf("task\n");
}

int main(void)
{
	arch::irq::init();
	sandwich::sched::init();
	uart::init();
	bcm2837::mbox::init();

	arch::irq::enable();

	sandwich::sched::task_t task("task", sched_task);
	task.wakeup();

	for (int i = 0; i < 8; i++)
		sandwich::sched::run();

	return 0;
}

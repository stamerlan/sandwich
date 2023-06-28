#include <cerrno>
#include <cstdio>
#include <bcm2837_mbox.h>
#include <sandwich/sched.h>
#include <uart.h>

static void sched_task(void)
{
	printf("task\n");
}

int main(void)
{
	uart::init();
	sandwich::sched::init();
	bcm2837::mbox::init();

	sandwich::sched::task_t task("task", sched_task);
	task.wakeup();

	alignas(16) volatile char get_serial_msg[] = {
		0x20, 0x00, 0x00, 0x00, /* message size in bytes */
		0x00, 0x00, 0x00, 0x00, /* request code */

		0x04, 0x00, 0x01, 0x00, /* get serial tag */
		0x08, 0x00, 0x00, 0x00, /* buffer size for serial */
		0x00, 0x00, 0x00, 0x00, /* request */
		0x00, 0x00, 0x00, 0x00, /* buffer for serial number */
		0x00, 0x00, 0x00, 0x00,

		0x00, 0x00, 0x00, 0x00, /* end tag */
	};
	while (bcm2837::mbox::send(get_serial_msg) == -EAGAIN);

	for (int i = 0; i < 8; i++)
		sandwich::sched::run();

	return 0;
}

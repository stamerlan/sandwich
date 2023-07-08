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

	sandwich::sched::task_t task("task", sched_task);
	task.wakeup();

	arch::irq::enable();

	auto mbox_msg_ptr = bcm2837::mbox::msg_t::alloc(28,
		[](bcm2837::mbox::msg_t& self) {
			printf("mbox board revision:");
			for (size_t i = 0; i < 7; i++)
				printf(" %08x", self[i]);
			printf("\n");
			self.free(self);
		});
	auto& mbox_msg = *mbox_msg_ptr;
	mbox_msg[0] = 0x1c;     /* message size in bytes */
	mbox_msg[1] = 0x00;     /* request code */
	mbox_msg[2] = 0x010002; /* get board revision tag */
	mbox_msg[3] = 0x04;     /* buffer size for response */
	mbox_msg[4] = 0x00;     /* request */
	mbox_msg[5] = 0x00;     /* response buffer */
	mbox_msg[6] = 0x00;     /* end tag */

	printf("send mbox msg@%p...\n", mbox_msg_ptr);
	while (mbox_msg.send() == -EAGAIN);

	printf("run scheduler...\n");
	for (int i = 0; i < 8; i++)
		sandwich::sched::run();

	printf("Trigger data abort...\n");
	volatile int *r = (int *)0xFFFFFFFF00000000;
	*r = 0x100500;

	return 0;
}

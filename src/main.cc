#include <cerrno>
#include <cstdio>
#include <bcm2837_mbox.h>
#include <sandwich/sched.h>
#include <uart.h>

#include <cstdint>
static volatile uint32_t* const arm_intr = (uint32_t *)0x3F00'B200;
static volatile uint32_t* const arm_base_irq_en = (uint32_t *)0x3F00'B218;

static unsigned get_current_el(void)
{
	unsigned current_el;
	__asm volatile("mrs	%0, CurrentEL\n\t" : "=r"(current_el));
	return (current_el & 0xC) >> 2;
}

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

	printf("cpu0 EL%u\n", get_current_el());

	/* Set to enable ARM Mailbox IRQ. Write 1b set register */
	*arm_base_irq_en = 1u << 1;
	printf("ARM INTR: 0x%08x\n", *arm_intr);

#if 0
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
#else
	alignas(16) volatile char get_board_rev_msg[] = {
		0x1C, 0x00, 0x00, 0x00, /* message size in bytes */
		0x00, 0x00, 0x00, 0x00, /* request code */

		0x02, 0x00, 0x01, 0x00, /* get board revision tag */
		0x04, 0x00, 0x00, 0x00, /* buffer size for response */
		0x00, 0x00, 0x00, 0x00, /* request */
		0x00, 0x00, 0x00, 0x00, /* response buffer */

		0x00, 0x00, 0x00, 0x00, /* end tag */
	};
	while (bcm2837::mbox::send(get_board_rev_msg) == -EAGAIN);
#endif
	printf("ARM INTR: 0x%08x\n", *arm_intr);

	for (int i = 0; i < 8; i++)
		sandwich::sched::run();

	return 0;
}

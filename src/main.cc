#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <arch/irq.h>
#include <bcm2837_mbox.h>
#include <sandwich/sched.h>
#include <uart.h>

static unsigned get_current_el(void)
{
	unsigned current_el;
	asm volatile("mrs	%0, CurrentEL\n\t" : "=r"(current_el));
	return (current_el & 0xC) >> 2;
}

static void sched_task(void)
{
	printf("task\n");
}

#define PRIx64 "lx"
extern "C" void curr_el_spx_sync(uint64_t esr, uint64_t elr, uint64_t spsr,
	uint64_t far)
{
	printf("Synchronous: ");
	switch(esr>>26) {
	case 0b000000: printf("Unknown"); break;
	case 0b000001: printf("Trapped WFI/WFE"); break;
	case 0b001110: printf("Illegal execution"); break;
	case 0b010101: printf("System call"); break;
	case 0b100000: printf("Instruction abort, lower EL"); break;
	case 0b100001: printf("Instruction abort, same EL"); break;
	case 0b100010: printf("Instruction alignment fault"); break;
	case 0b100100: printf("Data abort, lower EL"); break;
	case 0b100101: printf("Data abort, same EL"); break;
	case 0b100110: printf("Stack alignment fault"); break;
	case 0b101100: printf("Floating point"); break;
	default: printf("Unknown"); break;
	}

	/* decode data abort cause */
	if(esr>>26==0b100100 || esr>>26==0b100101) {
		printf(", ");
		switch((esr>>2)&0x3) {
		case 0: printf("Address size fault"); break;
		case 1: printf("Translation fault"); break;
		case 2: printf("Access flag fault"); break;
		case 3: printf("Permission fault"); break;
		}
		switch(esr&0x3) {
		case 0: printf(" at level 0"); break;
		case 1: printf(" at level 1"); break;
		case 2: printf(" at level 2"); break;
		case 3: printf(" at level 3"); break;
		}
	}

	/* dump registers */
	printf("\n");
	printf("ESR_EL1:  0x%" PRIx64 "\n", esr);
	printf("ELR_EL1:  0x%" PRIx64 "\n", elr);
	printf("SPSR_EL1: 0x%" PRIx64 "\n", spsr);
	printf("FAR_EL1:  0x%" PRIx64 "\n", far);

	for (;;);
}

int main(void)
{
	arch::irq::init();
	sandwich::sched::init();
	uart::init();
	bcm2837::mbox::init();

	printf("cpu0 EL%u\n", get_current_el());
	sandwich::sched::task_t task("task", sched_task);
	task.wakeup();

	arch::irq::enable();

	/* Set to enable ARM Mailbox IRQ. Write 1b set register */
#if 0
	alignas(16) volatile char mbox_msg[] = {
		0x20, 0x00, 0x00, 0x00, /* message size in bytes */
		0x00, 0x00, 0x00, 0x00, /* request code */

		0x04, 0x00, 0x01, 0x00, /* get serial tag */
		0x08, 0x00, 0x00, 0x00, /* buffer size for serial */
		0x00, 0x00, 0x00, 0x00, /* request */
		0x00, 0x00, 0x00, 0x00, /* buffer for serial number */
		0x00, 0x00, 0x00, 0x00,

		0x00, 0x00, 0x00, 0x00, /* end tag */
	};
#else
	alignas(16) volatile char mbox_msg[] = {
		0x1C, 0x00, 0x00, 0x00, /* message size in bytes */
		0x00, 0x00, 0x00, 0x00, /* request code */

		0x02, 0x00, 0x01, 0x00, /* get board revision tag */
		0x04, 0x00, 0x00, 0x00, /* buffer size for response */
		0x00, 0x00, 0x00, 0x00, /* request */
		0x00, 0x00, 0x00, 0x00, /* response buffer */

		0x00, 0x00, 0x00, 0x00, /* end tag */
	};
#endif
	printf("send mbox msg@%p...\n", mbox_msg);
	while (bcm2837::mbox::send(mbox_msg) == -EAGAIN);

	printf("run scheduler...\n");
	for (int i = 0; i < 8; i++)
		sandwich::sched::run();

	printf("Trigger data abort...\n");
	volatile int *r = (int *)0xFFFFFFFF00000000;
	*r = 0x100500;

	return 0;
}

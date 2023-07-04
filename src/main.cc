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

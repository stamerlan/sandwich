#include <bcm2837_mbox.h>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <sandwich/sched.h>

static constexpr uintptr_t perepherial_base = 0x3F00'0000;
static constexpr uintptr_t mbox_base = perepherial_base + 0x0000'B880;

/* The read register for mailbox 0.
 * Bits:
 * [31-4]: The 28 bits of data sent to the CPU.
 * [3-0]:  The mailbox channel number from which the data came from.
 */
static const volatile uint32_t* const mbox_read =
	(uint32_t *)(mbox_base + 0x00);

/* Status register for mailbox 0.
 * Bits:
 * [31]: Set if the mailbox is full, and thus no more data can be written to it.
 * [30]: Set if the mailbox is empty, and thus no more data is available to be
 *       read from it.
 */
static const volatile uint32_t * const mbox_status =
	(uint32_t *)(mbox_base + 0x18);
static constexpr uint32_t mbox_status_empty = 1u << 30;
static constexpr uint32_t mbox_status_full = 1u << 31;

/* Mailbox 0 configuration register.
 * Bits:
 * [0]: Enable interrupts.
 */
static volatile uint32_t * const mbox_conf = (uint32_t *)(mbox_base + 0x1C);

/* The write register for mailbox 0. Tthis is actually the read register for
 * mailbox 1.
 * Bits:
 * [31-4]: The 28 bits of data to be sent to the destination.
 * [3-0]:  The mailbox channel number to which the data is to be sent.
 */
static volatile uint32_t * const mbox_write = (uint32_t *)(mbox_base + 0x20);

/* Mailbox channel: property interface (ARM to VC) */
static constexpr uint32_t mbox_channel_props_out = 8u;

static void sched_mbox(void)
{
	if (*mbox_status & mbox_status_empty)
		return;

	uint32_t msg_addr = *mbox_read;
	unsigned channel = msg_addr & 0xFu;
	void *msg = reinterpret_cast<void *>(msg_addr & ~0xFu);

	printf("mbox ch:%u@%p\n", channel, msg);
}
static sandwich::sched::task_t mbox_task("bcm2837_mbox", sched_mbox);

void bcm2837::mbox::init(void)
{
	mbox_task.wakeup();
	*mbox_conf = 1;
}

int bcm2837::mbox::send(volatile void *msg)
{
	if (*mbox_status & mbox_status_full)
		return -EAGAIN;

	uintptr_t msg_addr = reinterpret_cast<uintptr_t>(msg);
	if (msg_addr & 0xFu)
		return -EINVAL;

	/* ensure message is written to memory */
	asm volatile("dmb st" ::: "memory");

	/* send message address to property interface */
	*mbox_write = msg_addr | mbox_channel_props_out;

	return 0;
}

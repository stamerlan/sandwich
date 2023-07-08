#include <bcm2837_mbox.h>
#include <cassert>
#include <cerrno>
#include <type_traits>
#include <arch/irq.h>
#include <sandwich/sched.h>

static constexpr size_t mbox_size_u32 =
	(CONFIG_BCM2837_MBOX_SIZE + sizeof(uint32_t) - 1) / sizeof(uint32_t);

static constexpr uintptr_t perepherial_base = 0x3F00'0000;
static constexpr uintptr_t mbox_base = perepherial_base + 0x0000'B880;

/* The read register for mailbox 0.
 * Bits:
 * [31-4]: The 28 bits of data sent to the CPU.
 * [3-0]:  The mailbox channel number from which the data came from.
 */
static const volatile uint32_t * const mbox_read =
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

static void sched_mbox(void);
static sandwich::sched::task_t mbox_task("bcm2837_mbox", sched_mbox);

static struct request_t : public bcm2837::mbox::msg_t {
	void (*cb)(struct bcm2837::mbox::msg_t& self);
	bool used;
	bool completed;
	alignas(16) volatile uint32_t buffer[mbox_size_u32];
} mbox_msg;
/* need for containerof usage */
static_assert(std::is_standard_layout_v<request_t>);

static void sched_mbox(void)
{
	if (mbox_task.sleep([](void) { return !mbox_msg.completed; }))
		return;

	mbox_msg.completed = false;
	mbox_msg.cb(mbox_msg);
}

static void mbox_isr(void)
{
	while (!(*mbox_status & mbox_status_empty)) {
		uint32_t msg_addr = *mbox_read;
		msg_addr &= ~0xFu;

		assert(reinterpret_cast<void *>(msg_addr) == mbox_msg.buffer);
		assert(!mbox_msg.completed);
		mbox_msg.completed = true;
		mbox_task.wakeup();
	}
}

struct bcm2837::mbox::msg_t *
bcm2837::mbox::msg_t::alloc(size_t msg_sz,
	void (*cb)(struct bcm2837::mbox::msg_t& self))
{
	if (mbox_msg.used)
		return nullptr;
	if (msg_sz > CONFIG_BCM2837_MBOX_SIZE)
		return nullptr;

	mbox_msg.used = true;
	mbox_msg.completed = false;
	mbox_msg.cb = cb;

	return &mbox_msg;
}

void bcm2837::mbox::msg_t::free(struct bcm2837::mbox::msg_t *msg)
{
	if (!msg)
		return;

	assert(msg == &mbox_msg);

	mbox_msg.used = false;
	mbox_msg.completed = false;
}

volatile uint32_t& bcm2837::mbox::msg_t::operator[](size_t ofs) noexcept
{
	assert(ofs < mbox_size_u32);
	return mbox_msg.buffer[ofs];
}

int bcm2837::mbox::msg_t::send(void) noexcept
{
	if (*mbox_status & mbox_status_full)
		return -EAGAIN;

	/* ensure message is written to memory */
	asm volatile("dmb st" ::: "memory");

	/* send message address to property interface */
	uintptr_t msg_addr = reinterpret_cast<uintptr_t>(mbox_msg.buffer);
	*mbox_write = msg_addr | mbox_channel_props_out;

	return 0;
}

void bcm2837::mbox::init(void)
{
	mbox_task.wakeup();
	*mbox_conf = 1;

	arch::irq::irq_en(1, mbox_isr);
}

#ifndef DRIVERS_BCM2837_MBOX_H
#define DRIVERS_BCM2837_MBOX_H

#include <cstddef>
#include <cstdint>
#include <config.h>

namespace bcm2837::mbox {

struct msg_t {
	static struct msg_t *alloc(size_t msg_sz,
		void (*cb)(struct msg_t& self)) noexcept;
	static void free(struct msg_t& msg) noexcept;

	msg_t(void) = default;
	msg_t(const msg_t&) = delete;
	msg_t(msg_t&&) = delete;
	msg_t& operator=(const msg_t&) = delete;
	msg_t& operator=(msg_t&&) = delete;

	volatile uint32_t& operator[](size_t) noexcept;
	int send(void) noexcept;
};

#ifdef CONFIG_BCM2837_MBOX

void init(void);

#else /* CONFIG_BCM2837_MBOX */

static void init(void) {}

#endif /* CONFIG_BCM2837_MBOX */

} /* namespace bcm2837::mbox */

#endif /* DRIVERS_BCM2837_MBOX_H */

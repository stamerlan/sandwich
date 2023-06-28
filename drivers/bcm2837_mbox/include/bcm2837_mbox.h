#ifndef DRIVERS_BCM2837_MAILBOX_H
#define DRIVERS_BCM2837_MAILBOX_H

#include <config.h>

namespace bcm2837::mbox {

#ifdef CONFIG_BCM2837_MBOX

void init(void);
int send(volatile void *msg);

#else /* CONFIG_BCM2837_MBOX */

#include <cerrno>

static void init(void) {}
static int send(volatile void *msg) {
	(void)msg;
	return -ENOSYS;
}

#endif /* CONFIG_BCM2837_MBOX */

} /* namespace bcm2837::mbox */

#endif /* DRIVERS_BCM2837_MAILBOX_H */

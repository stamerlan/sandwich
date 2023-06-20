#include <arch/irq.h>

arch::irq::flags_t arch::irq::disable(void)
{
	return 0;
}

void arch::irq::enable(arch::irq::flags_t flags)
{
	(void)flags;
}

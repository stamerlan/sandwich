#include <arch/irq.h>

arch::irq::flags arch::irq::disable(void)
{
	return 0;
}

void arch::irq::enable(arch::irq::flags flags)
{
	(void)flags;
}

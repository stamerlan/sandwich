#include <arch/irq.h>

void arch::irq::init(void)
{
}

void irq_en(unsigned irq_nr)
{
	(void)irq_nr;
}

void irq_en(unsigned irq_nr, void (*isr)(void))
{
	(void)irq_nr;
	(void)isr;
}

arch::irq::flags_t arch::irq::disable(void)
{
	return 0;
}

void arch::irq::enable(void)
{
}

void arch::irq::enable(arch::irq::flags_t flags)
{
	(void)flags;
}

#include <arch/irq.h>

static constexpr arch::irq::flags DAIF_I_BIT = 0x80;

arch::irq::flags arch::irq::disable(void)
{
	arch::irq::flags flags;
	asm volatile(
		"mrs	%0, daif\n"
		"msr	daifset, #2"
		: "=r"(flags) :: "memory"
	);
	return flags;
}

void arch::irq::enable(arch::irq::flags flags)
{
	if (flags & DAIF_I_BIT)
		return;
	asm volatile("msr	daifclr, #2" ::: "memory");
}

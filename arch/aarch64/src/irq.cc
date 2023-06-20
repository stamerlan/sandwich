#include <arch/irq.h>

static constexpr arch::irq::flags_t DAIF_I_BIT = 0x80;

arch::irq::flags_t arch::irq::disable(void)
{
	arch::irq::flags_t flags;
	asm volatile(
		"mrs	%0, daif\n"
		"msr	daifset, #2"
		: "=r"(flags) :: "memory"
	);
	return flags;
}

void arch::irq::enable(arch::irq::flags_t flags)
{
	if (flags & DAIF_I_BIT)
		return;
	asm volatile("msr	daifclr, #2" ::: "memory");
}

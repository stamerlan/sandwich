#include <arch/irq.h>
#include <cstddef>
#include <cstdint>

extern "C" char vectors[];
extern "C" void dummy_irq_handler(void) {}
void irq_0_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_1_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_2_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_3_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_4_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_5_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_6_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_7_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_8_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_9_handler(void)  __attribute__((weak, alias("dummy_irq_handler")));
void irq_10_handler(void) __attribute__((weak, alias("dummy_irq_handler")));
void irq_11_handler(void) __attribute__((weak, alias("dummy_irq_handler")));
void irq_12_handler(void) __attribute__((weak, alias("dummy_irq_handler")));
void irq_13_handler(void) __attribute__((weak, alias("dummy_irq_handler")));
void irq_14_handler(void) __attribute__((weak, alias("dummy_irq_handler")));
void irq_15_handler(void) __attribute__((weak, alias("dummy_irq_handler")));

void (*irq_table[])(void) = {
	irq_0_handler,
	irq_1_handler,
	irq_2_handler,
	irq_3_handler,
	irq_4_handler,
	irq_5_handler,
	irq_6_handler,
	irq_7_handler,
	irq_8_handler,
	irq_9_handler,
	irq_10_handler,
	irq_11_handler,
	irq_12_handler,
	irq_13_handler,
	irq_14_handler,
	irq_15_handler,
};

void arch::irq::init(void)
{
	asm volatile("msr	vbar_el1, %0\n\t" :: "r"(vectors));
}

void arch::irq::irq_en(unsigned irq_nr)
{
	static volatile uint32_t *const arm_base_irq_en = (uint32_t *)0x3F00'B218;
	/* Set to enable IRQ. Write 1b set register */
	*arm_base_irq_en = 1u << irq_nr;
}

void arch::irq::irq_en(unsigned irq_nr, void (*isr)(void))
{
	irq_table[irq_nr] = isr;
	irq_en(irq_nr);
}

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

void arch::irq::enable(void)
{
	asm volatile("msr	daifclr, #2" ::: "memory");
}

void arch::irq::enable(arch::irq::flags_t flags)
{
	static constexpr arch::irq::flags_t DAIF_I_BIT = 0x80;
	if (flags & DAIF_I_BIT)
		return;
	asm volatile("msr	daifclr, #2" ::: "memory");
}

extern "C" void curr_el_spx_irq(uint64_t esr, uint64_t elr, uint64_t spsr,
	uint64_t far)
{
	(void)esr;
	(void)elr;
	(void)spsr;
	(void)far;

	static volatile uint32_t *const arm_base_irq_pending = (uint32_t *)0x3F00'B200;

	uint32_t pending = *arm_base_irq_pending;
	for (size_t i = 0; i < sizeof(irq_table) / sizeof(irq_table[0]); i++)
		if (pending & (1u << i))
			irq_table[i]();
}

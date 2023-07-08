#ifndef ARCH_AARCH64_EXCEPTION_LVL_H
#define ARCH_AARCH64_EXCEPTION_LVL_H

namespace arch::aarch64 {

static unsigned current_el(void)
{
	unsigned current_el;
	asm volatile("mrs	%0, CurrentEL\n\t" : "=r"(current_el));
	return (current_el & 0xC) >> 2;
}

} /* namespace arch::aarch64 */

#endif /* ARCH_AARCH64_EXCEPTION_LVL_H */

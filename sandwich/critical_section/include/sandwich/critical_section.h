#ifndef SANDWICH_CRITICAL_SECTION_H
#define SANDWICH_CRITICAL_SECTION_H

#include <arch/irq.h>

namespace sandwich {

/**
 * @brief Wrapper to disable/enable IRQ on local CPU.
 * The class provides a convinient RAII-style mechanism for makeing critical
 * section. Interrupts on local CPU are disabled for the duration of a scoped
 * block.
 */
class critical_section_t {
public:
	critical_section_t(void) : flags(arch::irq::disable()) {}
	critical_section_t(const critical_section_t&) = delete;
	critical_section_t(critical_section_t&&) = delete;
	critical_section_t& operator=(const critical_section_t&) = delete;
	critical_section_t& operator=(critical_section_t&&) = delete;

	~critical_section_t(void)
	{
		arch::irq::enable(flags);
	}
private:
	arch::irq::flags_t flags;
};

} /* namespace sandwich */

#endif /* SANDWICH_CRITICAL_SECTION_H */

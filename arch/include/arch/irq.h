#ifndef ARCH_IRQ_H
#define ARCH_IRQ_H

namespace arch::irq {

/**
 * @brief Integral type to represent an interrupt subsystem state.
 */
using flags_t = unsigned long;

/**
 * @brief Disable interrupt handling.
 * @return current interrupt subsystem state.
 */
flags_t disable(void);

/**
 * @brief Enable interrupt handling.
 */
void enable(void);

/**
 * @brief Enable interrupt handling if flags.
 * If interrupts where disabled before disable() call, interrupts remain
 * disabled.
 * @param flags: flags returned by disable() call.
 */
void enable(flags_t flags);

} /* namespace arch::irq */

#endif /* ARCH_IRQ_H */

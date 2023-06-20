#ifndef ARCH_IRQ_H
#define ARCH_IRQ_H

namespace arch::irq {

/**
 * @brief Integral type to represent an interrupt subsystem state.
 */
using flags = unsigned long;

/**
 * @brief Disable interrupt handling.
 * @return current interrupt subsystem state.
 */
flags disable(void);

/**
 * @brief Enable interrupt handling.
 * If interrupts where disabled before disable() call, interrupts remain
 * disabled.
 * @param flags: flags returned by disable() call.
 */
void enable(flags flags);

} /* namespace arch::irq */

#endif /* ARCH_IRQ_H */

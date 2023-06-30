#ifndef ARCH_IRQ_H
#define ARCH_IRQ_H

namespace arch::irq {

/**
 * @brief Integral type to represent an interrupt subsystem state.
 */
using flags_t = unsigned long;

/**
 * @brief Initialize interrupt controller and setup interrupt vectors.
 */
void init(void);

/**
 * @brief Enable IRQ.
 * @param irq_nr: irq number.
 */
void irq_en(unsigned irq_nr);

/**
 * @brief Enable IRQ and set handler.
 * @param irq_nr: irq number.
 * @param isr: interrupt handler.
 */
void irq_en(unsigned irq_nr, void (*isr)(void));

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

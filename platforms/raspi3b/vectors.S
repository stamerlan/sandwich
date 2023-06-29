	/* Save all general purpose registers to stack */
.macro armv8_save_regs
	sub	sp, sp, 32 * 8
	stp	x0,  x1,  [sp, 16 * 0]
	stp	x2,  x3,  [sp, 16 * 1]
	stp	x4,  x5,  [sp, 16 * 2]
	stp	x6,  x7,  [sp, 16 * 3]
	stp	x8,  x9,  [sp, 16 * 4]
	stp	x10, x11, [sp, 16 * 5]
	stp	x12, x13, [sp, 16 * 6]
	stp	x14, x15, [sp, 16 * 7]
	stp	x16, x17, [sp, 16 * 8]
	stp	x18, x19, [sp, 16 * 9]
	stp	x20, x21, [sp, 16 * 10]
	stp	x22, x23, [sp, 16 * 11]
	stp	x24, x25, [sp, 16 * 12]
	stp	x26, x27, [sp, 16 * 13]
	stp	x28, x29, [sp, 16 * 14]
	str	x30, [sp, 16 * 15]
.endm /* armv8_save_regs */


	/* ARMv8 vector table entry.
	 * Save registers, call isr, restore registers, return from interrupt.
	 * ISR prototype:
	 * void isr(uint64_t esr, uint64_t elr, uint64_t spsr, uint64_t far);
	 */
.macro	armv8_vte, isr
	armv8_save_regs

	mrs	x0, esr_el1
	mrs	x1, elr_el1
	mrs	x2, spsr_el1
	mrs	x3, far_el1
	bl	\isr
	b	armv8_eret
.endm /* armv8_interrupt_table_entry */


	/* Load all general purpose registers from stack and return from
	 * exception
	 */
armv8_eret:
	ldp	x0,  x1,  [sp, 16 * 0]
	ldp	x2,  x3,  [sp, 16 * 1]
	ldp	x4,  x5,  [sp, 16 * 2]
	ldp	x6,  x7,  [sp, 16 * 3]
	ldp	x8,  x9,  [sp, 16 * 4]
	ldp	x10, x11, [sp, 16 * 5]
	ldp	x12, x13, [sp, 16 * 6]
	ldp	x14, x15, [sp, 16 * 7]
	ldp	x16, x17, [sp, 16 * 8]
	ldp	x18, x19, [sp, 16 * 9]
	ldp	x20, x21, [sp, 16 * 10]
	ldp	x22, x23, [sp, 16 * 11]
	ldp	x24, x25, [sp, 16 * 12]
	ldp	x26, x27, [sp, 16 * 13]
	ldp	x28, x29, [sp, 16 * 14]
	ldr	x30, [sp, 16 * 15]
	add	sp, sp, 32 * 8

	eret


	.balign 0x800
	.global vectors
vectors:
	/* The exception handler for a synchronous exception from the current EL
	 * using SP0.
	 */
	armv8_vte curr_el_sp0_sync

	/* The exception handler for an IRQ exception from the current EL using
	 * SP0.
	 */
	.balign 0x80
	armv8_vte curr_el_sp0_irq

	/* The exception handler for an FIQ exception from the current EL using
	 * SP0.
	 */
	.balign 0x80
	armv8_vte curr_el_sp0_fiq

	/* The exception handler for a System Error exception from the current
	 * EL using SP0.
	 */
	.balign 0x80
	armv8_vte curr_el_sp0_serror

	/* The exception handler for a synchrous exception from the current EL
	 * using the current SP.
	 */
	.balign 0x80
	armv8_vte curr_el_spx_sync

	/* The exception handler for an IRQ exception from the current EL using
	 * the current SP.
	 */
	.balign 0x80
	armv8_vte curr_el_spx_irq

	/* The exception handler for an FIQ from the current EL using the
	 * current SP.
	 */
	.balign 0x80
	armv8_vte curr_el_spx_fiq

	/* The exception handler for a System Error exception from the current
	 * EL using the current SP.
	 */
	.balign 0x80
	armv8_vte curr_el_spx_serror

	/* Unused handlers */
#if 0
	/* The exception handler for a synchronous exception from a lower EL
	 * (AArch64).
	 */
	.balign 0x80
	armv8_vte lower_el_aarch64_sync

	/* The exception handler for an IRQ from a lower EL (AArch64). */
	.balign 0x80
	armv8_vte lower_el_aarch64_irq

	/* The exception handler for an FIQ from a lower EL (AArch64). */
	.balign 0x80
	armv8_vte lower_el_aarch64_fiq

	/* The exception handler for a System Error exception from a lower
	 * EL(AArch64). */
	.balign 0x80
	armv8_vte lower_el_aarch64_serror

	/* The exception handler for a synchronous exception from a lower EL
	 * (AArch32).
	 */
	.balign 0x80
	armv8_vte lower_el_aarch32_sync

	/* The exception handler for an IRQ from a lower EL (AArch32). */
	.balign 0x80
	armv8_vte lower_el_aarch32_irq

	/* The exception handler for an FIQ from a lower EL (AArch32). */
	.balign 0x80
	armv8_vte lower_el_aarch32_fiq

	/* The exception handler for a System Error exception from a lower
	 * EL(AArch32). */
	.balign 0x80
	armv8_vte lower_el_aarch32_serror
#endif

	.weak	curr_el_sp0_sync
	.weak	curr_el_sp0_irq
	.weak	curr_el_sp0_fiq
	.weak	curr_el_sp0_serror
	.weak	curr_el_spx_sync
	.weak	curr_el_spx_irq
	.weak	curr_el_spx_fiq
	.weak	curr_el_spx_serror
	.weak	lower_el_aarch64_sync
	.weak	lower_el_aarch64_irq
	.weak	lower_el_aarch64_fiq
	.weak	lower_el_aarch64_serror
	.weak	lower_el_aarch32_sync
	.weak	lower_el_aarch32_irq
	.weak	lower_el_aarch32_fiq
	.weak	lower_el_aarch32_serror
curr_el_sp0_sync:
curr_el_sp0_irq:
curr_el_sp0_fiq:
curr_el_sp0_serror:
curr_el_spx_sync:
curr_el_spx_irq:
curr_el_spx_fiq:
curr_el_spx_serror:
lower_el_aarch64_sync:
lower_el_aarch64_irq:
lower_el_aarch64_fiq:
lower_el_aarch64_serror:
lower_el_aarch32_sync:
lower_el_aarch32_irq:
lower_el_aarch32_fiq:
lower_el_aarch32_serror:
	b	_halt

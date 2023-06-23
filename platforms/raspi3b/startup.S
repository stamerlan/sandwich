.section ".startup", "ax", @progbits

.global _start
.global _halt

_start:
	/* Read CPU ID */
	mrs	x0, mpidr_el1
	and	x0, x0, #3
	cbz	x0, 1f

_halt:	/* CPU ID > 0 */
	wfe
	b	_halt

1:	/* CPU ID == 0 */
	/* Check current exception level */
	mrs	x0, currentEL
	cmp	x0, #0b1000    /* EL is stored in bits[3:2] */
	beq	el2_entry
	blo	el1_entry

el3_entry: /* CPU0 at EL3 */
	/* Init SCTLR_EL2 and HCR_EL2 to save values before entering EL2 */
	msr	SCTLR_EL2, xzr
	msr	HCR_EL2, xzr

	/* Determine the EL2 Execution state */
	mrs	x0, SCR_EL3
	orr	x0, x0, #(1<<10) /* RW EL2 Execution state is AArch64 */
	orr	x0, x0, #(1<<0)  /* NS EL1 is Non-secure world. */
	msr	SCR_EL3, x0
	mov	x0, #0b01001     /* DAIF=0000 */
	msr	SPSR_EL3, x0     /* M[4:0]=01001 EL2h must match SCR_EL3.RW */

	/* Determine EL2 entry */
	adr	x0, el2_entry    /* el2_entry points to the first instruction */
	msr	ELR_EL3, x0      /* of EL2 code */

	eret

el2_entry: /* CPU at EL2 */
#if 0
	/* Initialize the SCTLR_EL1 register before entering EL1 */
	msr	SCTLR_EL1, xzr

	/* Determine the EL1 Execution state */
	mrs	x0, HCR_EL2
	orr	x0, x0, #(1<<31) /* RW=1 EL1 Execution state is AArch64 */
	msr	HCR_EL2, x0
	mov	x0, #0b00101     /* DAIF=0000 */
	msr	SPSR_EL2, x0     /* M[4:0]=00101 EL1h must match HCR_EL2.RW */

	/* Determine EL1 entry */
	adr	x0, el1_entry    /* el1_entry points to the first instruction */
	msr	ELR_EL2, x0      /* of EL1 code */

	eret
#endif

el1_entry: /* CPU at EL1 */
	/* Setup stack */
	ldr	x0, =__stack_base__
	mov	sp, x0

	/* Hook function to init memory */
	bl	_cpu_init_hook

	/* Zero the memory in the .bss section */
	ldr	x0, =__bss_start__ /* memset first arg: start of memory block */
	mov	w1, #0             /* memset second arg: fill balue */
	ldr	x2, =__bss_end__
	sub	x2, x2, x0         /* memset third arg" length of block */
	bl	memset

	/* Init standard library */
	bl	__libc_init_array

	bl	main
	b	exit


	.weak	_cpu_init_hook
	.weak	_init
	.weak	_fini
_cpu_init_hook:
_init:
_fini:
	ret

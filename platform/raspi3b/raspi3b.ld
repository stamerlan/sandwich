ENTRY(_start)

MEMORY {
	SDRAM (rwx) : ORIGIN = 0, LENGTH = 512M
}

SECTIONS
{
	/* Startup code should be placed first and located at 0x80000 */
	.startup 0x80000 : {
		__stack_top = .;
		*(.startup)
	} > SDRAM

	.init_array : {
		__init_array_start = .;
		KEEP(*(.init_array*))
		/*KEEP(*(.ctors*))*/
		__init_array_end = .;
	} > SDRAM

	.text : { *(.text*) } > SDRAM
	.rodata : { *(.rodata*) } > SDRAM
	.data : { *(.data*) } > SDRAM

	.bss (NOLOAD) : {
		__bss_start = .;
		*(.bss*)
		*(COMMON)
		__bss_end = .;
	} > SDRAM


	/DISCARD/ : {
		*(.comment)
		*(.gnu*)
		*(.note*)
		*(.eh_frame*)
		*(.ARM.exidx*)
	}
}

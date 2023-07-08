#define __int64_t_defined 1

#include <cinttypes>
#include <cstdint>
#include <cstdio>

extern "C" void curr_el_spx_sync(uint64_t esr, uint64_t elr, uint64_t spsr,
	uint64_t far)
{
	printf("Synchronous: ");
	switch(esr>>26) {
	case 0b000000: printf("Unknown"); break;
	case 0b000001: printf("Trapped WFI/WFE"); break;
	case 0b001110: printf("Illegal execution"); break;
	case 0b010101: printf("System call"); break;
	case 0b100000: printf("Instruction abort, lower EL"); break;
	case 0b100001: printf("Instruction abort, same EL"); break;
	case 0b100010: printf("Instruction alignment fault"); break;
	case 0b100100: printf("Data abort, lower EL"); break;
	case 0b100101: printf("Data abort, same EL"); break;
	case 0b100110: printf("Stack alignment fault"); break;
	case 0b101100: printf("Floating point"); break;
	default: printf("Unknown"); break;
	}

	/* decode data abort cause */
	if(esr>>26==0b100100 || esr>>26==0b100101) {
		printf(", ");
		switch((esr>>2)&0x3) {
		case 0: printf("Address size fault"); break;
		case 1: printf("Translation fault"); break;
		case 2: printf("Access flag fault"); break;
		case 3: printf("Permission fault"); break;
		}
		switch(esr&0x3) {
		case 0: printf(" at level 0"); break;
		case 1: printf(" at level 1"); break;
		case 2: printf(" at level 2"); break;
		case 3: printf(" at level 3"); break;
		}
	}

	/* dump registers */
	printf("\n");
	printf("ESR_EL1:  0x%" PRIx64 "\n", esr);
	printf("ELR_EL1:  0x%" PRIx64 "\n", elr);
	printf("SPSR_EL1: 0x%" PRIx64 "\n", spsr);
	printf("FAR_EL1:  0x%" PRIx64 "\n", far);

	for (;;);
}

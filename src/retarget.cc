#include <errno.h>
//#include "uart.h"

#define MMIO_BASE       0x3F000000

#define GPFSEL1         ((volatile unsigned int*)(MMIO_BASE+0x00200004))
#define GPPUD           ((volatile unsigned int*)(MMIO_BASE+0x00200094))
#define GPPUDCLK0       ((volatile unsigned int*)(MMIO_BASE+0x00200098))

/* Auxilary mini UART registers */
#define AUX_ENABLE      ((volatile unsigned int*)(MMIO_BASE+0x00215004))
#define AUX_MU_IO       ((volatile unsigned int*)(MMIO_BASE+0x00215040))
#define AUX_MU_IER      ((volatile unsigned int*)(MMIO_BASE+0x00215044))
#define AUX_MU_IIR      ((volatile unsigned int*)(MMIO_BASE+0x00215048))
#define AUX_MU_LCR      ((volatile unsigned int*)(MMIO_BASE+0x0021504C))
#define AUX_MU_MCR      ((volatile unsigned int*)(MMIO_BASE+0x00215050))
#define AUX_MU_LSR      ((volatile unsigned int*)(MMIO_BASE+0x00215054))
#define AUX_MU_MSR      ((volatile unsigned int*)(MMIO_BASE+0x00215058))
#define AUX_MU_SCRATCH  ((volatile unsigned int*)(MMIO_BASE+0x0021505C))
#define AUX_MU_CNTL     ((volatile unsigned int*)(MMIO_BASE+0x00215060))
#define AUX_MU_STAT     ((volatile unsigned int*)(MMIO_BASE+0x00215064))
#define AUX_MU_BAUD     ((volatile unsigned int*)(MMIO_BASE+0x00215068))

namespace uart {
/**
 * Set baud rate and characteristics (115200 8N1) and map to GPIO
 */
static void init(void)
{
	unsigned int r;

	/* initialize UART */
	*AUX_ENABLE = *AUX_ENABLE | 1;       // enable UART1, AUX mini uart
	*AUX_MU_CNTL = 0;
	*AUX_MU_LCR = 3;       // 8 bits
	*AUX_MU_MCR = 0;
	*AUX_MU_IER = 0;
	*AUX_MU_IIR = 0xc6;    // disable interrupts
	*AUX_MU_BAUD = 270;    // 115200 baud
	/* map UART1 to GPIO pins */
	r=*GPFSEL1;
	r&=~((7<<12)|(7<<15)); // gpio14, gpio15
	r|=(2<<12)|(2<<15);    // alt5
	*GPFSEL1 = r;
	*GPPUD = 0;            // enable pins 14 and 15
	r=150; while(r--) { asm volatile("nop"); }
	*GPPUDCLK0 = (1<<14)|(1<<15);
	r=150; while(r--) { asm volatile("nop"); }
	*GPPUDCLK0 = 0;        // flush GPIO setup
	*AUX_MU_CNTL = 3;      // enable Tx, Rx
}

/**
 * Send a character
 */
void putchar(int c) {
	/* wait until we can send */
	do{asm volatile("nop");}while(!(*AUX_MU_LSR&0x20));
	/* write the character to the buffer */
	*AUX_MU_IO=c;
}

} /* namespace uart */

extern "C" void *_sbrk(int incr)
{
	/* TODO: Find _sbrk/malloc() calls. printf? */
	(void)incr;

	return nullptr;
}

extern "C" int _write(int file, char *ptr, int len)
{
	(void)file;

	static bool uart_init_done;
	if (!uart_init_done) {
		uart::init();
		uart_init_done = true;
	}

	for (int i = 0; i < len; i++, ptr++) {
		if (*ptr == '\n')
			uart::putchar('\r');
		uart::putchar(*ptr);
	}

	return len;
}

extern "C" int _read(int file, char *ptr, int len)
{
	(void)file;
	(void)ptr;
	(void)len;

	errno = ENOSYS;
	return -1;
}

extern "C" int _close(int file)
{
	(void)file;

	errno = ENOSYS;
	return -1;
}

extern "C" int _fstat(int file, struct stat *st)
{
	(void)file;
	(void)st;

	errno = ENOSYS;
	return -1;
}

extern "C" int _isatty(int file)
{
	(void)file;

	errno = ENOSYS;
	return 0;
}

extern "C" int _lseek(int file, int ptr, int dir)
{
	(void)file;
	(void)ptr;
	(void)dir;

	errno = ENOSYS;
	return -1;
}

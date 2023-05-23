#include <uart.h>
#include <cstdint>
#include <cstdio>

/* TODO: Use device tree for register description */
/* https://cs140e.sergio.bz/docs/BCM2837-ARM-Peripherals.pdf */
__attribute__((unused)) static constexpr uintptr_t MMIO_BASE       = 0x3F00'0000;

/* GPIO registers */
__attribute__((unused)) static constexpr uintptr_t GPIO_BASE       = MMIO_BASE + 0x20'0000;
__attribute__((unused)) static volatile  uint32_t *GPFSEL0         = (uint32_t *)(GPIO_BASE + 0x00);
__attribute__((unused)) static volatile  uint32_t *GPFSEL1         = (uint32_t *)(GPIO_BASE + 0x04);
__attribute__((unused)) static volatile  uint32_t *GPFSEL2         = (uint32_t *)(GPIO_BASE + 0x08);
__attribute__((unused)) static volatile  uint32_t *GPFSEL3         = (uint32_t *)(GPIO_BASE + 0x0C);
__attribute__((unused)) static volatile  uint32_t *GPFSEL4         = (uint32_t *)(GPIO_BASE + 0x10);
__attribute__((unused)) static volatile  uint32_t *GPFSEL5         = (uint32_t *)(GPIO_BASE + 0x14);
__attribute__((unused)) static volatile  uint32_t *GPSET0          = (uint32_t *)(GPIO_BASE + 0x1C);
__attribute__((unused)) static volatile  uint32_t *GPSET1          = (uint32_t *)(GPIO_BASE + 0x20);
__attribute__((unused)) static volatile  uint32_t *GPCLR0          = (uint32_t *)(GPIO_BASE + 0x28);
__attribute__((unused)) static volatile  uint32_t *GPCLR1          = (uint32_t *)(GPIO_BASE + 0x2C);
__attribute__((unused)) static volatile  uint32_t *GPLEV0          = (uint32_t *)(GPIO_BASE + 0x34);
__attribute__((unused)) static volatile  uint32_t *GPLEV1          = (uint32_t *)(GPIO_BASE + 0x38);
__attribute__((unused)) static volatile  uint32_t *GPEDS0          = (uint32_t *)(GPIO_BASE + 0x40);
__attribute__((unused)) static volatile  uint32_t *GPEDS1          = (uint32_t *)(GPIO_BASE + 0x44);
__attribute__((unused)) static volatile  uint32_t *GPREN0          = (uint32_t *)(GPIO_BASE + 0x4C);
__attribute__((unused)) static volatile  uint32_t *GPREN1          = (uint32_t *)(GPIO_BASE + 0x50);
__attribute__((unused)) static volatile  uint32_t *GPFEN0          = (uint32_t *)(GPIO_BASE + 0x58);
__attribute__((unused)) static volatile  uint32_t *GPFEN1          = (uint32_t *)(GPIO_BASE + 0x5C);
__attribute__((unused)) static volatile  uint32_t *GPHEN0          = (uint32_t *)(GPIO_BASE + 0x64);
__attribute__((unused)) static volatile  uint32_t *GPHEN1          = (uint32_t *)(GPIO_BASE + 0x68);
__attribute__((unused)) static volatile  uint32_t *GPLEN0          = (uint32_t *)(GPIO_BASE + 0x70);
__attribute__((unused)) static volatile  uint32_t *GPLEN1          = (uint32_t *)(GPIO_BASE + 0x74);
__attribute__((unused)) static volatile  uint32_t *GPAREN0         = (uint32_t *)(GPIO_BASE + 0x7C);
__attribute__((unused)) static volatile  uint32_t *GPAREN1         = (uint32_t *)(GPIO_BASE + 0x80);
__attribute__((unused)) static volatile  uint32_t *GPAFEN0         = (uint32_t *)(GPIO_BASE + 0x88);
__attribute__((unused)) static volatile  uint32_t *GPAFEN1         = (uint32_t *)(GPIO_BASE + 0x8C);
__attribute__((unused)) static volatile  uint32_t *GPPUD           = (uint32_t *)(GPIO_BASE + 0x94);
__attribute__((unused)) static volatile  uint32_t *GPPUDCLK0       = (uint32_t *)(GPIO_BASE + 0x98);
__attribute__((unused)) static volatile  uint32_t *GPPUDCLK1       = (uint32_t *)(GPIO_BASE + 0x9C);

/* Auxilary mini UART registers */
__attribute__((unused)) static constexpr uintptr_t AUX_BASE        = MMIO_BASE + 0x21'5000;
__attribute__((unused)) static volatile  uint32_t *AUX_IRQ         = (uint32_t *)(AUX_BASE + 0x00);
__attribute__((unused)) static volatile  uint32_t *AUX_ENABLES     = (uint32_t *)(AUX_BASE + 0x04);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_IO_REG   = (uint32_t *)(AUX_BASE + 0x40);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_IER_REG  = (uint32_t *)(AUX_BASE + 0x44);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_IIR_REG  = (uint32_t *)(AUX_BASE + 0x48);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_LCR_REG  = (uint32_t *)(AUX_BASE + 0x4C);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_MCR_REG  = (uint32_t *)(AUX_BASE + 0x50);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_LSR_REG  = (uint32_t *)(AUX_BASE + 0x54);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_MSR_REG  = (uint32_t *)(AUX_BASE + 0x58);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_SCRATCH  = (uint32_t *)(AUX_BASE + 0x5C);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_CNTL_REG = (uint32_t *)(AUX_BASE + 0x60);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_STAT_REG = (uint32_t *)(AUX_BASE + 0x64);
__attribute__((unused)) static volatile  uint32_t *AUX_MU_BAUD     = (uint32_t *)(AUX_BASE + 0x68);

/* TODO: move to arch code */
static void delay(unsigned cycles)
{
	for (size_t i = 0; i < cycles; i++)
		asm volatile("nop");
}

void uart::init(void)
{
	/* TODO: Calculate baud rate depending on cpu freq.
	 * See "BCM2837 ARM Peripherals" section 2.2.1 "Mini UART implementation
	 * details":
	 *   baudrate = system clock freq / (8 * (baudrate_reg + 1))
	 *
	 * https://cs140e.sergio.bz/docs/BCM2837-ARM-Peripherals.pdf
	 */

	*AUX_ENABLES     = *AUX_ENABLES | 1;   /* enable UART1, AUX mini uart */
	*AUX_MU_CNTL_REG = 0;
	*AUX_MU_LCR_REG  = 3;                  /* 8 bits */
	*AUX_MU_MCR_REG  = 0;
	*AUX_MU_IER_REG  = 0;
	*AUX_MU_IIR_REG  = 0xc6;               /* disable interrupts */
	*AUX_MU_BAUD     = 270;                /* 115200 baud */

	/* TODO: Move to GPIO driver */
	/* Map UART1 to GPIO pins */
	uint32_t gpfsel1 = *GPFSEL1;
	gpfsel1 &= ~((7u << 12) | (7u << 15)); /* gpio14, gpio15 */
	gpfsel1 |= (2u << 12) | (2u << 15);    /* alt5 */
	*GPFSEL1 = gpfsel1;
	*GPPUD = 0;                            /* disable pull-up/down */
	/* Wait 150 cycles: this provides the required set-up time for the
	 * control signal.
	 */
	delay(150);
	*GPPUDCLK0 = *GPPUDCLK0 | (1u << 14) | (1u << 15);
	/* Wait 150 cycles: this provides the required set-up time for the
	 * control signal.
	 */
	delay(150);
	/* Write to GPPUD to remove the control signal */

	/* Write to GPPUDCLK0/1 to remove the clock */
	*GPPUDCLK0 = 0;

	/* Enable uart receiver and transmitter */
	*AUX_MU_CNTL_REG = 3;
}

int uart::putchar(int c)
{
	if (!(*AUX_MU_LSR_REG & 0x20))
		return EOF;

	c = (unsigned char)c;
	*AUX_MU_IO_REG = c;
	return c;
}

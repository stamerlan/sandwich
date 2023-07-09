#include <uart.h>
#include <cassert>
#include <cstdint>
#include <bcm2837_mbox.h>

static constexpr uintptr_t MMIO_BASE       = 0x3F00'0000;
static constexpr uintptr_t GPIO_BASE       = MMIO_BASE + 0x20'0000;

static volatile uint32_t * const UART0_DR =
	(uint32_t *)(MMIO_BASE + 0x0020'1000);
static volatile uint32_t * const UART0_FR =
	(uint32_t *)(MMIO_BASE + 0x0020'1018);
static volatile uint32_t * const UART0_IBRD =
	(uint32_t *)(MMIO_BASE + 0x0020'1024);
static volatile uint32_t * const UART0_FBRD =
	(uint32_t *)(MMIO_BASE + 0x0020'1028);
static volatile uint32_t * const UART0_LCHR =
	(uint32_t *)(MMIO_BASE + 0x0020'102C);
static volatile uint32_t * const UART0_CR  =
	(uint32_t *)(MMIO_BASE + 0x0020'1030);
static volatile uint32_t * const UART0_ICR =
	(uint32_t *)(MMIO_BASE + 0x0020'1044);

static volatile uint32_t * const GPFSEL1   = (uint32_t *)(GPIO_BASE + 0x04);
static volatile uint32_t * const GPPUD     = (uint32_t *)(GPIO_BASE + 0x94);
static volatile uint32_t * const GPPUDCLK0 = (uint32_t *)(GPIO_BASE + 0x98);

/* TODO: move to arch code */
static void delay(unsigned cycles)
{
	for (size_t i = 0; i < cycles; i++)
		asm volatile("nop");
}

bool uart::init(void)
{
	static enum class state {
		disable_uart0,
		alloc_mbox_msg,
		send_mbox_msg,
		wait_mbox_cpl,
		setup_gpio,
	} init_state;
	static bcm2837::mbox::msg_t *set_clk_msg;

	uint32_t gpfsel1;

	switch (init_state) {
	case state::disable_uart0:
		*UART0_CR = 0;
		init_state = state::alloc_mbox_msg;
		[[fallthrough]];

	case state::alloc_mbox_msg:
		set_clk_msg = bcm2837::mbox::msg_t::alloc(36,
			[](bcm2837::mbox::msg_t& msg) {
				/* TODO: Check response code */
				init_state = state::setup_gpio;
				bcm2837::mbox::msg_t::free(msg);
				set_clk_msg = nullptr;
			});
		if (!set_clk_msg)
			break;

		(*set_clk_msg)[0] = 36;          /* message size */
		(*set_clk_msg)[1] = 0;           /* requeset */
		(*set_clk_msg)[2] = 0x0003'8002; /* tag: set clk rate */
		(*set_clk_msg)[3] = 12;          /* parameters size */
		(*set_clk_msg)[4] = 0;           /* request */
		(*set_clk_msg)[5] = 2;           /* param0: clk id */
		(*set_clk_msg)[6] = 4'000'000;   /* param1: rate 4MHz */
		(*set_clk_msg)[7] = 0;           /* param2: skip turbo */
		(*set_clk_msg)[8] = 0;           /* tag: end */

		init_state = state::send_mbox_msg;
		[[fallthrough]];

	case state::send_mbox_msg:
		if (!set_clk_msg->send())
			init_state = state::wait_mbox_cpl;
		break;

	case state::wait_mbox_cpl:
		break;

	case state::setup_gpio:
		/* map UART0 to GPIO pins */
		gpfsel1 = *GPFSEL1;
		gpfsel1 &= ~((7u << 12) | (7u << 15)); /* gpio14, gpio15 */
		gpfsel1 |= (4u << 12) | (4u << 15);    /* alt0 */
		*GPFSEL1 = gpfsel1;

		*GPPUD = 0;                           /* disable pull-up/down */
		/* Wait 150 cycles: this provides the required set-up time for
		 * the control signal.
		 */
		delay(150);

		/* enable pins 14 and 15 */
		*GPPUDCLK0 = *GPPUDCLK0 | (1u << 14) | (1u << 15);
		/* Wait 150 cycles: this provides the required set-up time for
		 * the control signal.
		 */
		delay(150);

		/* Write to GPPUDCLK0/1 to remove the clock */
		*GPPUDCLK0 = 0;

		*UART0_ICR  = 0x7FF;                   /* clear interrupts */
		*UART0_IBRD = 2;                       /* 115200 baud rate */
		*UART0_FBRD = 8;
		*UART0_LCHR = 7u << 4;                 /* 8n1, enable FIFO */
		*UART0_CR   = 0x301;                   /* enable TX, RX, UART */

		init_state = state::disable_uart0;
		return true;

	default:
		assert(false);
	}

	return false;
}

int uart::putchar(int c)
{
	c = (unsigned char)c;
	while (*UART0_FR & 0x20)
		asm volatile("nop");
	*UART0_DR = c;
	return c;
}

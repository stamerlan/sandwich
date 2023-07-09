#ifndef DRIVERS_UART_H
#define DRIVERS_UART_H

#include <config.h>

namespace uart {

#ifdef CONFIG_UART
bool init(void);
int putchar(int c);
#else
static inline bool init(void) { return true; }
static inline int putchar(int c) { return (unsigned char)c; }
#endif

} /* namespace uart */

#endif /* DRIVERS_UART_H */

#include <cerrno>
#include <cstdio>
#include <uart.h>

extern "C" void *_sbrk(int incr)
{
	/* TODO: Find _sbrk/malloc() calls. printf? */
	(void)incr;

	return nullptr;
}

extern "C" int _write(int file, char *ptr, int len)
{
	(void)file;

	for (int i = 0; i < len; i++, ptr++) {
		if (*ptr == '\n')
			while (uart::putchar('\r') == EOF)
				asm volatile("nop");
		while (uart::putchar(*ptr) == EOF)
			asm volatile("nop");
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

extern "C" int _getpid(void)
{
	return 0;
}

extern "C" int _kill(int pid, int sig)
{
	(void)pid;
	(void)sig;

	errno = ENOSYS;
	return -1;
}

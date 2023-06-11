extern "C"
[[ noreturn ]]
void init(void)
{
	extern char __bss_start[];
	extern char __bss_end[];

	for (char* p = __bss_start; p < __bss_end; p++)
		*p = 0;

	/* call constructors of static objects */
	extern void (*__init_array_start) (void);
	extern void (*__init_array_end) (void);
	for (void (**ctor)(void) = &__init_array_start; ctor < &__init_array_end; ctor++)
		(**ctor)();

	int main(void);
	main();

	for (;;);
}

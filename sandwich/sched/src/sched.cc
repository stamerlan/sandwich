#include <sched/sched.h>
#include <algorithm>
#include <cstdio>
#include <type_traits>

static_assert(std::is_standard_layout<sandwich::sched::detail::task_t>::value);

/* Defined in linker script. Array of pointers to task_t. */
extern "C" sandwich::sched::detail::task_t * const __start_sandwich_task_ptr[];
extern "C" sandwich::sched::detail::task_t * const __stop_sandwich_task_ptr[];

void sandwich::sched::init(void)
{
	printf("tasks ptrs section: [%p:%p]\n", __start_sandwich_task_ptr,
		__stop_sandwich_task_ptr);
	size_t tasks_ptrs_sz = uintptr_t(__stop_sandwich_task_ptr) -
		uintptr_t(__start_sandwich_task_ptr);

	for (size_t i = 0; i < tasks_ptrs_sz; i += 16) {
		size_t print_bytes = std::min(size_t(16), tasks_ptrs_sz - i);

		printf("0x%04zx:", i);

		auto p = (const unsigned char *)__start_sandwich_task_ptr + i;
		for (size_t j = 0; j < print_bytes; j++)
			printf(" %02x", p[j]);
		for (size_t j = print_bytes; j < 16; j++)
			printf("   ");

		printf(" | ");
		for (size_t j = 0; j < print_bytes; j++) {
			char c = p[j];
			if (c < ' ' || c > '~')
				c = '.';
			printf("%c", c);
		}
		for (size_t j = print_bytes; j < 16; j++)
			printf(" ");
		printf("|\n");
	}

	auto task_ptr = __start_sandwich_task_ptr;
	for (; task_ptr < __stop_sandwich_task_ptr; task_ptr++)
		printf("task@%p: %s\n", *task_ptr, (*task_ptr)->name);
}

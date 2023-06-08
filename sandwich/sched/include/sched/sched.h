#ifndef SANDWICH_SCHED_H
#define SANDWICH_SCHED_H

namespace sandwich::sched {

void init(void);

namespace detail {
struct task_t {
	const char *name;
	struct task_t *next;

	bool (*fn)(void);
};
} /* namespace sandwich::sched::detail */

} /* namespace sandwich::sched */

#define SANDWICH_TASK(handler)                                        \
	__attribute__((used)) static       \
	sandwich::sched::detail::task_t sandwich_task_ ## handler = { \
		.name = #handler,                                     \
		.next = nullptr,                                      \
		.fn   = handler                                       \
	}; \
	\
	__attribute__((section(".sandwich_task_ptr"),used)) static \
	sandwich::sched::detail::task_t * const sandwich_task_ ## handler ## _ptr = &sandwich_task_ ## handler

#endif /* SANDWICH_SCHED_H */

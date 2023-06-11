#ifndef SANDWICH_SCHED_H
#define SANDWICH_SCHED_H

namespace sandwich::sched {

struct task_t {
	const char *name;
	struct task_t *next;
	bool (*fn)(void);
};

/**
 * @brief Initialize cooperative scheduler.
 */
void init(void);

/**
 * @brief Schedule task for execution.
 * @param task: task to be executed.
 *
 * @todo Make thread-safe.
 */
void wakeup(struct task_t *task);

/**
 * @brief Execute next task.
 *
 * @todo Make thread-safe.
 */
void run(void);

} /* namespace sandwich::sched */

#define SANDWICH_TASK(handler)                                \
	__attribute__((used)) static                          \
	sandwich::sched::task_t sandwich_task_ ## handler = { \
		.name  = #handler,                            \
		.next  = nullptr,                             \
		.fn    = handler                              \
	}

#endif /* SANDWICH_SCHED_H */

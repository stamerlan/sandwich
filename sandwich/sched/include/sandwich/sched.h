#ifndef SANDWICH_SCHED_H
#define SANDWICH_SCHED_H

/**
 * @page sandwich_sched Scheduling
 *
 * Sandwich uses cooperative scheduler. The scheduler determines which task is
 * allowed to execute at any point in time on current CPU. This task is known as
 * **current task**.
 *
 * Scheduler selects and executes next task on sandwich::sched::run() call.
 *
 * @section scheduling_usage Usage example
 * @code{.cpp}
 * #include <sandwich/sched.h>
 *
 * static void task_handler(void);
 * static sandwich::sched::task_t task("task", task_handler);
 *
 * // Task handler. Invoked by scheduler.
 * // Run task 10 times and enter sleep forever.
 * static void task_handler(void)
 * {
 * 	static int run_cnt = 0;
 *
 * 	if (++run_cnt < 10)
 * 		printf("Task\n");
 * 	else
 * 		task.sleep();
 * }
 *
 * void main(void)
 * {
 * 	// Initialize scheduler
 * 	sandwich::sched::init();
 *
 * 	// Tasks are created in sleep state. Wake up.
 * 	task.wakeup();
 *
 * 	// Run scheduler forever
 * 	for(;;)
 * 		sandwich::sched::run();
 * }
 * @endcode
 *
 * @section sandwich_sched_algo Scheduling Algorithm
 * Scheduler read queue implemented as a simple list. Selecting next task to
 * execute, add task to run queue and remove task from run queue is done for
 * O(1).
 *
 * @section sandwich_sched_tasks Tasks
 * Task is a unit of execution or unit of work. It is represented by
 * sandwich::sched::task_t. The task object must exist while task is scheduled
 * for execution or executing. Typically tasks are defined at compile time and
 * exist whole application life-time.
 */
namespace sandwich::sched {

class task_t final {
public:
	task_t(const char *name_, void (*handler_)(void));
	task_t(const task_t&) = delete;
	task_t(task_t&&) = delete;
	task_t& operator=(const task_t&) = delete;
	task_t& operator=(task_t&&) = delete;

	/**
	 * @brief Schedule task for execution on local CPU.
	 * Add task to scheduler run queue. If task is already in run queue do
	 * nothing.
	 * @note Safe to call from ISR.
	 */
	void wakeup(void);

	/**
	 * @brief Stop task execution.
	 * @note Safe to call from ISR.
	 */
	void sleep(void);

	/**
	 * @brief Atomically check condition and put task to sleep state.
	 * Predicate is executed with interrupts disabled on local CPU.
	 *
	 * Usage example:
	 *
	 * @code{.cpp}
	 * void task_handler(void);
	 * sandwich::sched::task_t task("example", task_handler);
	 *
	 * // ISR: schedule task if there are some data available
	 * static void fifo_isr(void)
	 * {
	 * 	task.wakeup();
	 * }
	 *
	 * // Task to process data in FIFO. Sleep if FIFO is empty.
	 * void task_handler(void)
	 * {
	 * 	// Put task to sleep if FIFO is empty
	 * 	if (task.sleep([](void) { return rx_fifo_empty; }))
	 * 		return;
	 *
	 * 	// Handle RX FIFO
	 * }
	 * @endcode
	 *
	 * @param predicate: Condition to check. If condition is true put task
	 *   to sleep state.
	 * @return The value returned by predicate.
	 */
	bool sleep(bool (*predicate)(void));

private:
	char name[16];
	void (* const handler)(void);

	volatile task_t *prev;
	volatile task_t *next;

	friend void run(void);
};

/**
 * @brief Initialize cooperative scheduler.
 */
void init(void);

/**
 * @brief Execute next task.
 */
void run(void);

} /* namespace sandwich::sched */

#endif /* SANDWICH_SCHED_H */

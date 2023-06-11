#include <sched/sched.h>
#include <type_traits>

static_assert(std::is_standard_layout_v<sandwich::sched::task_t>);

static sandwich::sched::task_t *next_task;

void sandwich::sched::init(void)
{
	next_task = nullptr;
}

void sandwich::sched::wakeup(struct task_t *task)
{
	if (task->state != sandwich::sched::task_state::sleep)
		return;

	if (!next_task) {
		/* it's the 1st task in run queue */
		next_task = task;
		task->next = task->prev = task;
	} else {
		next_task->prev->next = task;
		task->prev = next_task->prev;
		task->next = next_task;
		next_task->prev = task;
	}

	task->state = sandwich::sched::task_state::ready;
}

void sandwich::sched::run(void)
{
	if (!next_task)
		return;

	next_task->state = sandwich::sched::task_state::run;
	if (next_task->fn()) {
		/* Task remains in run queue. */
		next_task->state = sandwich::sched::task_state::ready;
		next_task = next_task->next;
	} else {
		/* Put the task to sleep state */
		if (next_task == next_task->next) {
			/* Current task is the only one task*/
			next_task = nullptr;
		} else {
			next_task->prev->next = next_task->next;
			next_task->next->prev = next_task->prev;
			next_task->state = sandwich::sched::task_state::sleep;

			next_task = next_task->next;
		}
	}
}

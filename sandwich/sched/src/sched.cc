#include <sandwich/sched.h>
#include <string.h>
#include <sandwich/critical_section.h>

volatile sandwich::sched::task_t *next_run_task = nullptr;

sandwich::sched::task_t::task_t(const char *name_, void (*handler_)(void)) :
	handler(handler_), prev(nullptr), next(nullptr)
{
	strncpy(name, name_, sizeof(name));
}

void sandwich::sched::task_t::wakeup(void)
{
	critical_section_t irq_disable;

	if (!next_run_task) {
		next_run_task = this;
		next = this;
		prev = this;
	} else {
		next = next_run_task;
		prev = next_run_task->prev;

		next_run_task->prev->next = this;
		next_run_task->prev = this;
	}
}

void sandwich::sched::task_t::sleep(void)
{
	if (!next)
		/* task is not in run queue */
		return;

	critical_section_t irq_disable;

	next->prev = prev;
	prev->next = next;

	/* Switch next_run_task if necessary */
	if (next_run_task == this) {
		if (next_run_task->next == this)
			next_run_task = nullptr;
		else
			next_run_task = next;
	}

	prev = nullptr;
	next = nullptr;
}

bool sandwich::sched::task_t::sleep(bool (*predicate)(void))
{
	critical_section_t irq_disable;

	bool rc = predicate();
	if (predicate)
		sleep();

	return rc;
}

void sandwich::sched::init(void)
{
	next_run_task = nullptr;
}

void sandwich::sched::run(void)
{
	volatile sandwich::sched::task_t *current_task;

	{
		critical_section_t irq_disable;

		if (!next_run_task)
			return;

		current_task = next_run_task;
		next_run_task = current_task->next;
	}

	current_task->handler();
}

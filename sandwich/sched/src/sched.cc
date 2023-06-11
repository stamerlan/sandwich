#include <sandwich/sched.h>
#include <type_traits>

static_assert(std::is_standard_layout_v<sandwich::sched::task_t>);

static sandwich::sched::task_t *head, *tail;

void sandwich::sched::init(void)
{
	head = tail = nullptr;
}

void sandwich::sched::wakeup(struct task_t *task)
{
	if (!head) {
		/* it's the 1st task in run queue */
		head = tail = task;
		task->next = task;
	} else {
		task->next = head;
		tail->next = task;
		tail = task;
	}
}

void sandwich::sched::run(void)
{
	if (!head)
		return;

	if (head->fn()) {
		tail = head;
		head = head->next;
	} else {
		/* Remove task from task queue */
		if (head->next == head) {
			/* If it's the only task running mark queue as empty */
			head = tail = nullptr;
		} else {
			head = head->next;
			tail->next = head;
		}
	}
}

#include <gtest/gtest.h>
#include <sandwich/sched.h>

static void task_a_handler(void);
static void task_b_handler(void);

static int task_a_cnt = 0;
static bool task_a_sleep = false;
static sandwich::sched::task_t task_a{"task_a", task_a_handler};

static int task_b_cnt = 0;
static bool task_b_sleep = false;
static sandwich::sched::task_t task_b{"task_b", task_b_handler};

static void task_a_handler(void)
{
	task_a_cnt++;
	if (task_a_sleep)
		task_a.sleep();
}

static void task_b_handler(void)
{
	task_b_cnt++;
	if (task_b_sleep)
		task_b.sleep();
}

class sched_test : public testing::Test {
protected:
	void SetUp(void) override
	{
		sandwich::sched::init();
		task_a_cnt = task_b_cnt = 0;
		task_a_sleep = task_b_sleep = false;
	}
};

TEST_F(sched_test, empty)
{
	/* Scheduler run queue is empty. Nothing expected to happen. */
	sandwich::sched::run();
	ASSERT_EQ(0, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);
}

TEST_F(sched_test, run_task)
{
	/* Schedule a single task. Check if task handler executed as many times
	 * as scheduler run.
	 */
	task_a.wakeup();

	for (int run_cnt = 1; run_cnt < 5; run_cnt++) {
		sandwich::sched::run();
		ASSERT_EQ(run_cnt, task_a_cnt);
		ASSERT_EQ(0, task_b_cnt);
	}
}

TEST_F(sched_test, run_two_tasks)
{
	/* Schedule two tasks. Tasks should be executed one-by-one on each
	 * scheduler run. */
	task_a.wakeup();
	task_b.wakeup();

	for (int run_cnt = 1; run_cnt < 10; run_cnt++) {
		sandwich::sched::run();
		ASSERT_EQ(run_cnt / 2 + (run_cnt % 2), task_a_cnt);
		ASSERT_EQ(run_cnt / 2, task_b_cnt);
	}
}

TEST_F(sched_test, run_task_forever_and_other_once)
{
	/* Schedule two tasks. One task runs forever, while other sleep after
	 * the first run.
	 */
	task_a.wakeup();
	task_b.wakeup();
	task_b_sleep = true;

	sandwich::sched::run();
	ASSERT_EQ(1, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);

	sandwich::sched::run();
	ASSERT_EQ(1, task_a_cnt);
	ASSERT_EQ(1, task_b_cnt);

	for (int run_cnt = 2; run_cnt < 5; run_cnt++) {
		sandwich::sched::run();
		ASSERT_EQ(run_cnt, task_a_cnt);
		ASSERT_EQ(1, task_b_cnt);
	}
}

TEST_F(sched_test, sleep)
{
	/* Schedule a single task. Task handler puts task to sleep state, it
	 * shouldn't be executed again.
	 */
	task_a.wakeup();
	task_a_sleep = true;

	sandwich::sched::run();
	ASSERT_EQ(1, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);

	sandwich::sched::run();
	ASSERT_EQ(1, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);
}

TEST_F(sched_test, sleep_if_predicate_true)
{
	/* Schedule a single task. Call task sleep with predicate true. Expected
	 * task is in sleep state.
	 */
	task_a.wakeup();

	sandwich::sched::run();
	ASSERT_EQ(1, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);

	task_a.sleep([](void){ return true; });
	sandwich::sched::run();
	ASSERT_EQ(1, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);
}

TEST_F(sched_test, sleep_if_predicate_false)
{
	/* Schedule a single task. Call task sleep with predicate false. Expected
	 * task is in running state.
	 */
	task_a.wakeup();

	sandwich::sched::run();
	ASSERT_EQ(1, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);

	task_a.sleep([](void){ return false; });
	sandwich::sched::run();
	ASSERT_EQ(2, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);
}

TEST_F(sched_test, wakeup_twice)
{
	/* Schedule a single task. Task handler puts task to sleep state. Task
	 * is woken up twice. It should be executed only once, enter sleep state
	 * and shouldn't be run until woken up again.
	 */
	task_a.wakeup();
	task_a_sleep = true;

	sandwich::sched::run();
	ASSERT_EQ(1, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);

	/* wake up twice */
	task_a.wakeup();
	task_a.wakeup();

	sandwich::sched::run();
	ASSERT_EQ(2, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);

	/* run again to ensure task is sleeping */
	sandwich::sched::run();
	ASSERT_EQ(2, task_a_cnt);
	ASSERT_EQ(0, task_b_cnt);
}

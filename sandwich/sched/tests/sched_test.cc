#include <gtest/gtest.h>
#include <sandwich/sched.h>

static bool task_a_ret;
static int task_a_cnt;
static bool task_b_ret;
static int task_b_cnt;

static bool task_a(void)
{
	task_a_cnt++;
	return task_a_ret;
}
SANDWICH_TASK(task_a);

static bool task_b(void)
{
	task_b_cnt++;
	return task_b_ret;
}
SANDWICH_TASK(task_b);

class sched_test : public testing::Test {
protected:
	void SetUp(void) override
	{
		sandwich::sched::init();

		task_a_ret = task_b_ret = false;
		task_a_cnt = task_b_cnt = 0;
	}
};

TEST_F(sched_test, empty)
{
	/* Scheduler run queue is empty. Nothing expected to happen. */
	sandwich::sched::run();
}

TEST_F(sched_test, wakeup)
{
	/* Schedule a single task. Check if task handler executed. */
	sandwich::sched::wakeup(&sandwich_task_task_a);
	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
}

TEST_F(sched_test, run_once)
{
	/* Schedule a single task. Task handler returns false, so it shouldn't
	 * be scheduled again.
	 */
	sandwich::sched::wakeup(&sandwich_task_task_a);
	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
}

TEST_F(sched_test, run_cont)
{
	/* Schedule a single task. Task handler returns true, so it should be
	 * scheduled again.
	 */
	task_a_ret = true;
	sandwich::sched::wakeup(&sandwich_task_task_a);
	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
	sandwich::sched::run();
	EXPECT_EQ(2, task_a_cnt);
}

TEST_F(sched_test, run_two)
{
	/* Schedule two tasks. Check if both tasks executed once */
	sandwich::sched::wakeup(&sandwich_task_task_a);
	sandwich::sched::wakeup(&sandwich_task_task_b);

	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
	EXPECT_EQ(0, task_b_cnt);

	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
	EXPECT_EQ(1, task_b_cnt);

	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
	EXPECT_EQ(1, task_b_cnt);
}

TEST_F(sched_test, run_once_and_cont)
{
	/* Schedule two tasks. task_a runs forever, task_b - only once. Check
	 * after task_b executed it is removed from run queue, only task_a
	 * remains.
	 */
	task_a_ret = true;
	sandwich::sched::wakeup(&sandwich_task_task_a);
	sandwich::sched::wakeup(&sandwich_task_task_b);

	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
	EXPECT_EQ(0, task_b_cnt);

	sandwich::sched::run();
	EXPECT_EQ(1, task_a_cnt);
	EXPECT_EQ(1, task_b_cnt);

	sandwich::sched::run();
	EXPECT_EQ(2, task_a_cnt);
	EXPECT_EQ(1, task_b_cnt);

	sandwich::sched::run();
	EXPECT_EQ(3, task_a_cnt);
	EXPECT_EQ(1, task_b_cnt);
}

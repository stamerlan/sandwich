#ifndef SANDWICH_SPINLOCK_H
#define SANDWICH_SPINLOCK_H

#include <atomic>

namespace sandwich {

/**
 * @brief Spinlock.
 * The most basic primitive for locking. A spinlock is a lock that causes a CPU
 * trying to acquire it to simply wait in a loop ("spin") while repeatedly
 * checking whether the lock is available.
 *
 * Spinlocks are used when wait times are expected to be short and when
 * contention is minimal.
 *
 * If you have a case where you have to protect a data structure across several
 * CPU's you can use spinlock IF you know that the spinlocks are never used in
 * interrupt handlers. Otherwise you need to disable interrupts first:
 * @msc
 *   task,ISR;
 *   task box task [label="spinlock.lock()"];
 *   task->ISR     [label="IRQ"];
 *   ISR box ISR   [label="spinlock.lock(); DEADLOCK"];
 * @endmsc
 */
class spinlock_t {
public:
	spinlock_t(void) = default;
	spinlock_t(const spinlock_t&) = delete;
	spinlock_t(spinlock_t&&) = delete;
	spinlock_t& operator=(const spinlock_t&) = delete;
	spinlock_t& operator=(spinlock_t&&) = delete;

	void lock(void) noexcept
	{
		for (;;) {
			/* Assume the lock is free on the first try */
			if (!atom.exchange(true, std::memory_order_acquire))
				return;

			/* Wait for lock to be released */
			while (atom.load(std::memory_order_relaxed)) {
				/* TODO: issue X86 PAUSE or ARM YIELD
				 * instruction to reduce contention between
				 * hyper-threads.
				 */
			}
		}
	}

	bool try_lock(void) noexcept
	{
		/* First do a relaxed load to check if lock is free in order to
		 * prevent unnecessary cache misses if someone does
		 * while(!try_lock())
		 */
		return !atom.load(std::memory_order_relaxed) &&
			!atom.exchange(true, std::memory_order_acquire);
	}

	void unlock(void) noexcept
	{
		atom.store(false, std::memory_order_release);
	}

protected:
	std::atomic<bool> atom{ false };
	static_assert(decltype(atom)::is_always_lock_free);
};

} /* namespace sandwich */

#endif /* SANDWICH_SPINLOCK_H */

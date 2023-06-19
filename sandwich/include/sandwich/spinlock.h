#ifndef SANDWICH_SPINLOCK_H
#define SANDWICH_SPINLOCK_H

#include <atomic>

namespace sandwich {

/**
 * @brief Simple spinlock implementation.
 * May be used to synchronize different CPUs. Disables interrupts while lock is
 * held.
 *
 * @todo: Disable interrupts until unlock() called.
 * @todo: Don't use atomic variable on uniprocessor systems.
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
};

} /* namespace sandwich */

#endif /* SANDWICH_SPINLOCK_H */

"""Fibonacci helpers. A run is 5 back-to-back Fibonacci numbers, up or down."""

from fibonacci_grid.config import FIB_RUN_LENGTH


def generate_fibonacci(max_value):
    """Return Fibonacci numbers up to max_value, with one 1: [1, 2, 3, 5, ...].

    Args:
        max_value (int): Largest number allowed.

    Returns:
        list[int]: The numbers, smallest first. Empty if max_value < 1.
    """
    fibs = []
    a, b = 1, 2
    while a <= max_value:
        fibs.append(a)
        a, b = b, a + b
    return fibs


def is_consecutive_fibonacci_run(values):
    """Check if values are back-to-back Fibonacci numbers, up or down.

    Args:
        values (list[int]): FIB_RUN_LENGTH numbers from neighbouring cells.

    Returns:
        bool: True if they form a run. A 0 always gives False.
    """
    values = list(values)
    if len(values) != FIB_RUN_LENGTH:
        return False
    if any(v < 1 for v in values):
        return False

    fibs = generate_fibonacci(max(values))
    for start in range(len(fibs) - FIB_RUN_LENGTH + 1):
        window = fibs[start:start + FIB_RUN_LENGTH]
        if values == window or values == window[::-1]:
            return True
    return False

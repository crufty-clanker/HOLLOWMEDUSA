"""Performance profiling utilities."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def profile(func: Callable) -> Callable:
    """Profile a function and print execution time."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__}: {end - start:.4f}s")
        return result

    return wrapper


def benchmark(func: Callable) -> Callable:
    """Run a function multiple times and report average time."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        iterations = 100
        times = []
        result = None
        for _ in range(iterations):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        avg = sum(times) / len(times)
        print(f"{func.__name__}: avg {avg:.6f}s over {iterations} iterations")
        return result

    return wrapper

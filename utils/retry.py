"""Simple retry decorator with optional page diagnostics on failures."""

import time


def retry(max_retries=3, delay=1, exceptions=(Exception,)):
    """Retry a callable with a fixed delay between attempts.

    Args:
        max_retries: Maximum number of attempts.
        delay: Delay in seconds between attempts.
        exceptions: Exception type or tuple of types that should trigger a retry.
    """
    def decorator(func):
        """Wrap a function with retry logic.

        Args:
            func: Callable to execute with retries.
        """
        def wrapper(*args, **kwargs):
            """Execute the function, retrying when exceptions occur.

            Args:
                *args: Positional arguments for the wrapped function.
                **kwargs: Keyword arguments for the wrapped function.
            """
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

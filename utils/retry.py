"""Simple retry decorator with optional page diagnostics on failures."""

import time


def retry(max_retries=3, delay=1):
    """Retry a callable with a fixed delay between attempts."""
    def decorator(func):
        """Wrap a function with retry logic."""
        def wrapper(*args, **kwargs):
            """Execute the function, retrying when exceptions occur."""
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

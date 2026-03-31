import time


def retry(max_retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    page = kwargs.get("page")
                    if page:
                        import os
                        os.makedirs("artifacts/screenshots", exist_ok=True)
                        os.makedirs("artifacts/html", exist_ok=True)
                        page.screenshot(path=f"artifacts/screenshots/retry_{attempt}.png")
                        html_content = page.content()
                        with open(f"artifacts/html/retry_{attempt}.html", "w", encoding="utf-8") as f:
                            f.write(html_content)
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator
import pytest
import os
from config.config_loader import ConfigLoader
import datetime

from utils.logger import get_logger
from utils.test_context import context

print("✅ conftest loaded")

@pytest.fixture(scope="session")
def config():
    env = os.getenv("TEST_ENV")
    return ConfigLoader(env=env)

@pytest.fixture(scope="session")
def logger():
    return get_logger()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    
    if report.failed:
        page = context.page
        logger = get_logger()
        test_name = item.nodeid.replace("/", "_").replace(":", "_").replace("::", "_")
        os.makedirs("artifacts/screenshots", exist_ok=True)
        if page:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")            
            path = f"artifacts/screenshots/failure_{test_name}_{timestamp}.png"
            try:
                page.screenshot(path=path)
                logger.error(f"Screenshot captures: {path}")
            except Exception as e:
                logger.error(f"Screenshot failed: {str(e)}")
        logger.error(f"Test failed: {test_name}")


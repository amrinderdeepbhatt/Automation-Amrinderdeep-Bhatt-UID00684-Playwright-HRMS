"""Shared pytest fixtures and failure reporting hooks for UI tests."""

import datetime
import os

import pytest

from config.config_loader import ConfigLoader

from utils.logger import get_logger
from utils.test_context import context

pytest_plugins = ("steps.test_shared_steps",)

@pytest.fixture(scope="session")
def config():
    """Load environment-specific framework configuration once per run."""
    env = os.getenv("TEST_ENV")
    return ConfigLoader(env=env)

@pytest.fixture(scope="session")
def logger():
    """Expose the framework logger as a session-level fixture."""
    return get_logger()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """Capture a screenshot and log details whenever a test fails.

    Args:
        item: Pytest test item for the current test case.
    """
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

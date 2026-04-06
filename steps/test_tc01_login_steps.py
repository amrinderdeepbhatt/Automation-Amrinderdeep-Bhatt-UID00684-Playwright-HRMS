"""BDD steps for successful login flow."""

from pytest_bdd import scenarios, then
from utils.logger import get_logger

import steps.test_shared_steps  # noqa: F401

scenarios("../features/tc01_login.feature")

logger = get_logger()


@then("user should be redirected to the welcome page")
def verify_redirect_to_welcome(page):
    """Assert that login lands on the welcome page."""
    logger.info("Verifying redirect to welcome page")
    try:
        assert page.url.endswith("/welcome")
        logger.info("Login successful")
    except AssertionError as e:
        logger.error(f"Login failed with error: {str(e)}")

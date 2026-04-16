"""BDD steps for login flow assertions."""

from pytest_bdd import parsers, scenarios, then
from playwright.sync_api import expect

import steps.test_shared_steps  # noqa: F401

from utils.logger import get_logger

scenarios("../features/tc01_login.feature")

logger = get_logger()


@then(parsers.parse("user should see {expected_result}"))
def verify_login_result(page, expected_result):
    """Assert the outcome for valid and invalid login attempts.

    Args:
        page: Active Playwright page.
        expected_result: Expected login outcome label from feature examples.
    """
    logger.info(f"Verifying login result: {expected_result}")

    if expected_result == "redirected to the welcome page":
        page.wait_for_url("**/index.php/index/welcome")
        logger.info("Login successful")
        return

    if expected_result == "invalid login error":
        error_text = "The username or password you entered is incorrect."
        error = page.locator("#usernameerror").filter(has_text=error_text).first
        error.wait_for(state="visible")
        expect(error).to_have_text(error_text)
        return

    raise AssertionError(f"Unsupported expected result: {expected_result}")

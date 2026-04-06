"""BDD steps for invalid login validation."""

from pytest_bdd import scenarios, then
from utils.logger import get_logger

import steps.test_shared_steps  # noqa: F401

scenarios("../features/tc02_login_invalid.feature")

logger = get_logger()


@then("user should see invalid login error")
def verify_invalid_login_error(page):
    """Verify the invalid-credentials error message is shown."""
    expected_text = "The username or password you entered is incorrect."
    logger.info("Verifying invalid login error message")
    error = page.locator("#usernameerror").filter(has_text=expected_text).first
    error.wait_for(state="visible", timeout=10000)
    assert error.inner_text().strip() == expected_text, "Invalid login error message not shown"

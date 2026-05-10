"""BDD steps for login flow assertions."""

import re

from pytest_bdd import scenarios, then
from playwright.sync_api import expect

import steps.test_shared_steps

from utils.logger import get_logger

scenarios("../features/tc01_login.feature")

logger = get_logger()


@then("user should be redirected to the welcome page")
def verify_valid_login_result(page):
    """Verify a successful login redirects to the welcome page.

    Args:
        page: Active Playwright page.
    """
    logger.info("Verifying valid login result")
    page.wait_for_url("**/index.php/index/welcome")
    expect(page).to_have_url(re.compile(r".*/index\.php/index/welcome$"))
    logger.info("Login successful")


@then("user should see an invalid login error")
def verify_invalid_login_result(page):
    """Verify an invalid login displays the expected error message.

    Args:
        page: Active Playwright page.
    """
    logger.info("Verifying invalid login result")
    error_text = "The username or password you entered is incorrect."
    from pages.login_page import LoginPage

    LoginPage(page).validate_invalid_login_error(error_text)

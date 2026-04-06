"""Shared one-action BDD steps reused across scenarios."""

from pytest_bdd import given, when
import pytest

from pages.base_page import BasePage
from pages.hr_page import HRPage
from pages.leave_page import LeavePage
from pages.login_page import LoginPage
from utils.credentials import load_login_credentials
from utils.logger import get_logger
from utils.test_context import context

logger = get_logger()


def _login(page, profile="valid"):
    """Sign in with the selected profile on the current page."""
    creds = load_login_credentials(profile)
    login_page = LoginPage(page)
    logger.info(f"Logging in with profile: {profile}")
    login_page.login(page.url, creds["username"], creds["password"])
    login_page.page.wait_for_load_state("networkidle")
    return login_page


@given("user opens the HRMS login page")
def given_open_login_page(page, config):
    """Open login page for authentication scenarios."""
    context.page = page
    BasePage(page).page.goto(config.get_url())


@when("user logs in with valid credentials from test data")
def when_login_valid(page):
    """Log in with valid credentials."""
    _login(page, profile="valid")


@when("user logs in with invalid credentials from test data")
def when_login_invalid(page):
    """Log in with invalid credentials."""
    _login(page, profile="invalid")


@when("user opens leave filter search")
def when_open_leave_filter_search(page):
    """Open leave grid search row."""
    page.locator("input.togglesearch").first.click()
    page.wait_for_load_state("networkidle")


@when("user opens Leave Request page")
def when_open_leave_request(page):
    """Navigate to Leave Request page from main menu."""
    LeavePage(page).navigate_to_leave_request()


@when("user opens My Leave page")
def when_open_my_leave(page):
    """Navigate to My Leave page from main menu."""
    LeavePage(page).navigate_to_my_leave()


@when("user opens HR section")
def when_open_hr_section(page):
    """Navigate to HR section from main menu."""
    HRPage(page).navigate_to_hr_section()


@pytest.fixture
def leave_ctx():
    """Provide mutable context for leave-related scenarios."""
    return {}

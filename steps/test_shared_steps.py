"""Shared one-action BDD steps reused across scenarios."""

import pytest
from pytest_bdd import given, parsers, when

from pages.base_page import BasePage
from pages.login_page import LoginPage
from utils.credentials import load_login_credentials
from utils.logger import get_logger
from utils.test_context import context

logger = get_logger()


def _login(page, profile="valid"):
    """Sign in with the selected profile on the current page.

    Args:
        page: Active Playwright page.
        profile: Credential profile key.
    """
    creds = load_login_credentials(profile)
    login_page = LoginPage(page)
    logger.info(f"Logging in with profile: {profile}")
    login_page.login(page.url, creds["username"], creds["password"])
    login_page.page.wait_for_load_state("networkidle")
    return login_page


@given("user opens the HRMS login page")
def given_open_login_page(page, config):
    """Open login page for authentication scenarios.

    Args:
        page: Active Playwright page.
        config: Loaded framework configuration.
    """
    context.page = page
    BasePage(page).page.goto(config.get_url())


@when(parsers.parse("user logs in with {profile} credentials from test data"))
def when_login_with_profile(page, profile):
    """Log in with a selected credential profile.

    Args:
        page: Active Playwright page.
        profile: Credential profile key.
    """
    _login(page, profile=profile)


@when("user opens leave filter search")
def when_open_leave_filter_search(page):
    """Open leave grid search row.

    Args:
        page: Active Playwright page.
    """
    page.locator("input.togglesearch").first.click()
    page.wait_for_load_state("networkidle")


@when("user opens Leave Request page")
def when_open_leave_request(page):
    """Navigate to Leave Request page from main menu.

    Args:
        page: Active Playwright page.
    """
    BasePage(page).navigate_main_menu("Self Service")


@when("user opens My Leave page")
def when_open_my_leave(page):
    """Navigate to My Leave page from main menu.

    Args:
        page: Active Playwright page.
    """
    base_page = BasePage(page)
    base_page.navigate_main_menu("Self Service")
    base_page.click("text=My Leave")
    page.wait_for_load_state("networkidle")


@when(parsers.parse('user navigates to "{menu_name}" from navigation bar'))
def when_navigate_from_main_nav(page, menu_name):
    """Navigate to a top-level menu by its label.

    Args:
        page: Active Playwright page.
        menu_name: Visible menu label to open.
    """
    BasePage(page).navigate_main_menu(menu_name)


@pytest.fixture
def leave_ctx():
    """Provide mutable context for leave-related scenarios."""
    return {}

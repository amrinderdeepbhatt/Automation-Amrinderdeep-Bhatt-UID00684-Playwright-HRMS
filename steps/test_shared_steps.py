"""Shared one-action BDD steps reused across scenarios."""

import pytest
from pytest_bdd import given, parsers, when
from urllib.parse import urljoin

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


@given(parsers.parse('user opens the {page_name} page at "{link}"'))
def given_open_named_page(page, config, page_name, link):
    """Open a named page by link using the reusable navigation step.

    Args:
        page: Active Playwright page.
        config: Loaded framework configuration.
        page_name: Human-readable page name (unused, informative).
        link: Absolute URL or site path to open.
    """
    # Navigate to the target link and set context.page.
    context.page = page
    base = config.get_url().rstrip("/")
    if link.startswith("http"):
        target = link
    elif link == "/":
        target = base
    else:
        target = urljoin(base + "/", link)
    BasePage(page).page.goto(target)
    BasePage(page).page.wait_for_load_state("networkidle")




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
    from pages.leave_page import LeavePage

    LeavePage(page).open_leave_filter_search()


@when(parsers.parse('user opens "{page_name}" page from "{menu_name}"'))
def when_open_page_from_menu(page, page_name, menu_name):
    """Navigate to a page by opening a menu and clicking the page item.

    Args:
        page: Active Playwright page.
        page_name: Visible text of the target page/link.
        menu_name: Top-level menu label to expand.
    """
    base_page = BasePage(page)
    base_page.navigate_main_menu(menu_name)
    base_page.click_text(page_name)
    page.wait_for_load_state("networkidle")


# Specific navigation steps are handled by the parameterized step above.


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

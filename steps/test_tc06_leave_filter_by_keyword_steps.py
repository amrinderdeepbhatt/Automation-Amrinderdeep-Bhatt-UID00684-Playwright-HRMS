"""BDD steps for filtering leave records by keyword."""

from pytest_bdd import scenarios, then, when
from playwright.sync_api import expect

import steps.test_shared_steps  # noqa: F401

from utils.logger import get_logger

logger = get_logger()

scenarios("../features/tc06_leave_filter.feature")


@when("user enters keyword in Leave Type filter")
def search_keyword(page):
    """Enter keyword in leave type search field.

    Args:
        page: Active Playwright page.
    """
    logger.info("Entering keyword 'Sick' in Leave type filter")

    type_field = page.locator("#leavetype")
    
    type_field.wait_for(state="visible")

    type_field.fill("Sick")
    type_field.press("Enter")
    

@then("leave data should be filtered as per the entered keyword")
def filtered_leave_data(page):
    """Validate that filtered rows match the keyword.

    Args:
        page: Active Playwright page.
    """
    sick_leaves = page.locator("#pendingleaves tbody tr td:nth-child(2) span").filter(has_text="Sick")
    count = sick_leaves.count()
    
    assert count > 0, f"Expected at least one 'Sick Leave' entry, but found {count}"

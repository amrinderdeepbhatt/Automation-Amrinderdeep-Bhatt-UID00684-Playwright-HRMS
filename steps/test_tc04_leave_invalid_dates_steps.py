"""BDD steps for validating invalid leave date ranges."""

from datetime import datetime, timedelta

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect
from pytest_bdd import parsers, scenarios, then, when

import steps.test_shared_steps  # noqa: F401
from pages.leave_page import LeavePage

scenarios("../features/tc04_leave_invalid_dates.feature")

def _select_leave_type_for_invalid_validation(page):
    """Select leave type for invalid date validation flow.

    Args:
        page: Active Playwright page.
    """
    leave_page = LeavePage(page)
    leave_page.select_leave_type("Annual Leave")
    leave_page.fill_reason()


@when("user opens create leave request modal from Apply Leave")
def open_leave_modal(page):
    """Open the leave modal for invalid date checks.

    Args:
        page: Active Playwright page.
    """
    LeavePage(page).open_create_leave_request_modal()


@when("user selects leave type for invalid date validation")
def select_leave_type_for_invalid_dates(page):
    """Select leave type and reason for invalid date validation.

    Args:
        page: Active Playwright page.
    """
    _select_leave_type_for_invalid_validation(page)


@when(parsers.parse("user enters leave dates with from offset {from_offset:d} and to offset {to_offset:d}"))
def fill_invalid_dates(page, from_offset, to_offset):
    """Fill from/to dates using parameterized offsets for validation checks.

    Args:
        page: Active Playwright page.
        from_offset: Day offset for From date.
        to_offset: Day offset for To date.
    """
    from_date = datetime.now() + timedelta(days=from_offset)
    to_date = datetime.now() + timedelta(days=to_offset)
    LeavePage(page).fill_invalid_leave_date_range(from_date, to_date)


@when("user submits leave request with invalid date range")
def submit_invalid_form(page):
    """Submit the leave form with invalid dates.

    Args:
        page: Active Playwright page.
    """
    LeavePage(page).submit_request()


@then("user should see invalid to-date validation error")
def verify_to_date_error(page):
    """Assert the expected to-date validation error appears.

    Args:
        page: Active Playwright page.
    """
    error = page.locator("#errors-to_date").first
    error.wait_for(state="visible")
    expect(error).to_contain_text("To date should be greater than from date.")

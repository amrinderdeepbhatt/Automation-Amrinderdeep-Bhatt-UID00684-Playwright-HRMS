"""BDD steps for validating invalid leave date ranges."""

from datetime import datetime, timedelta

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect
from pytest_bdd import parsers, scenarios, then, when

import steps.test_shared_steps
from pages.leave_page import LeavePage

scenarios("../features/tc04_leave_invalid_dates.feature")


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
    leave_page = LeavePage(page)
    leave_page.select_leave_type("Annual Leave")
    leave_page.fill_reason()


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
    LeavePage(page).fill_leave_date_range(from_date, to_date, valid_range=False)


@when("user submits leave request with invalid date range")
def submit_invalid_form(page):
    """Submit the leave form with invalid dates.

    Args:
        page: Active Playwright page.
    """
    LeavePage(page).submit_leave_form()


@then("user should see invalid to-date validation error")
def verify_to_date_error(page):
    """Assert the expected to-date validation error appears.

    Args:
        page: Active Playwright page.
    """
    error_text = LeavePage(page).get_field_error_text("#errors-to_date")
    assert error_text is not None
    assert "To date should be greater than from date." in error_text

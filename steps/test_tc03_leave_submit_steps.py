"""BDD steps for submitting a valid leave request."""

from utils.date_utils import date_from_offset as _date

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect
from pytest_bdd import scenarios, then, when

from pages.leave_page import LeavePage
from utils.test_data_factory import build_leave_date_window
from utils.retry import retry

import steps.test_shared_steps

scenarios("../features/tc03_leave_submit.feature")
@retry(max_retries=5, delay=0, exceptions=(RuntimeError, PlaywrightTimeoutError))
def _submit_leave_request_attempt(page):
    """Try once to fill and submit a leave request.

    Args:
        page: Active Playwright page.
    """
    leave_page = LeavePage(page)

    from_input = leave_page.dialog.locator(leave_page.FROM_DATE_SELECTOR).first

    start_offset, end_offset = build_leave_date_window(min_start=5, max_start=120, min_duration=1, max_duration=5)
    from_date = _date(start_offset)
    to_date = _date(end_offset)
    from_date, to_date = leave_page.normalize_leave_window(from_input, from_date, to_date)

    leave_page.submit_leave_request("Emergency Leave", None, from_date, to_date)

    try:
        page.wait_for_url("**/pendingleaves")
        return

    except PlaywrightTimeoutError:
        error_text = leave_page.get_submission_error_text()
        if error_text:
            if "already been applied" in error_text.lower():
                raise RuntimeError("Leave already applied for this date")

            raise AssertionError(f"Unexpected error: {error_text}")

        raise
@when("user opens create leave request modal from Apply Leave")
def open_leave_modal(page):
    """Open the create leave request modal from calendar.

    Args:
        page: Active Playwright page.
    """
    leave_page = LeavePage(page)
    leave_page.open_create_leave_request_modal()


@when("user enters leave details with valid date range")
def fill_leave_form(page):
    """Fill leave form with valid details and submit.

    Args:
        page: Active Playwright page.
    """
    _submit_leave_request_attempt(page)

@then("user should see leave request submission success")
def verify_leave_request_submitted(page):
    """Verify successful leave submission message and redirect.

    Args:
        page: Active Playwright page.
    """
    page.wait_for_url("**/pendingleaves")
    success = page.get_by_text("Leave request added successfully.", exact=False).first
    success.wait_for(state="visible")
    expect(success).to_be_visible()

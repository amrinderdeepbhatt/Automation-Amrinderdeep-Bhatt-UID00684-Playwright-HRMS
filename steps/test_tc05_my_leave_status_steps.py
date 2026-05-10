"""BDD steps for verifying status of an applied leave."""

from datetime import datetime
from utils.date_utils import date_from_offset as _date

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect
from pytest_bdd import scenarios, then, when

from pages.leave_page import LeavePage
from utils.retry import retry
from utils.test_data_factory import build_leave_date_window

import steps.test_shared_steps

scenarios("../features/tc05_my_leave_status.feature")

@retry(max_retries=5, delay=0, exceptions=(RuntimeError, PlaywrightTimeoutError))
def _submit_leave_request_attempt(page, leave_ctx):
    """Try once to fill and submit a leave request for status validation.

    Args:
        page: Active Playwright page.
        leave_ctx: Mutable fixture used to store leave data for later checks.
    """
    leave_page = LeavePage(page)
    from_input = leave_page.dialog.locator(leave_page.FROM_DATE_SELECTOR).first

    start_offset, end_offset = build_leave_date_window(min_start=5, max_start=120, min_duration=1, max_duration=2)
    from_date = _date(start_offset)
    to_date = _date(end_offset)
    from_date, to_date = leave_page.normalize_leave_window(from_input, from_date, to_date)

    leave_ctx["leave_type"] = "Emergency Leave"
    leave_ctx["from_date"] = from_date.strftime("%Y/%m/%d")
    leave_ctx["to_date"] = to_date.strftime("%Y/%m/%d")

    leave_ctx["reason"] = leave_page.submit_leave_request("Emergency Leave", None, from_date, to_date)

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


@when("user opens create leave request modal for status validation")
def open_leave_modal_for_status(page):
    """Open create leave request modal for status validation flow.

    Args:
        page: Active Playwright page.
    """
    LeavePage(page).open_create_leave_request_modal()


@when("user enters valid leave details for status validation")
def enter_leave_details_for_status(page, leave_ctx):
    """Enter leave details and submit for status validation.

    Args:
        page: Active Playwright page.
        leave_ctx: Mutable fixture used to store leave data for later checks.
    """
    _submit_leave_request_attempt(page, leave_ctx)

@then("the applied leave should appear in My Leave with status Pending for approval")
def verify_leave_status(page, leave_ctx):
    """Verify the applied leave appears with pending approval status.

    Args:
        page: Active Playwright page.
        leave_ctx: Mutable fixture containing stored leave data.
    """
    LeavePage(page).validate_pending_leave_submission(leave_ctx)

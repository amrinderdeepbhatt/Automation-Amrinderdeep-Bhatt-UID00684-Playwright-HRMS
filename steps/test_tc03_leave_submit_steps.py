"""BDD steps for submitting a valid leave request."""

from datetime import datetime, timedelta

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect
from pytest_bdd import scenarios, then, when

import steps.test_shared_steps  # noqa: F401
from pages.leave_page import LeavePage
from utils.test_context import context
from utils.test_data_factory import TestDataFactory
from utils.retry import retry

scenarios("../features/tc03_leave_submit.feature")


def _build_random_leave_window():
    """Generate a random valid date window for leave."""
    factory = TestDataFactory(seed=None)
    return factory.leave_date_offsets(min_start=5, max_start=120, min_duration=1, max_duration=5)


def _date(offset):
    """Return current datetime shifted by day offset.

    Args:
        offset: Number of days to shift from today.
    """
    return datetime.now() + timedelta(days=offset)


def _parse_prefilled_date(input_locator):
    """Parse a prefilled date value from input if available.

    Args:
        input_locator: Locator for date input.
    """
    raw_value = input_locator.input_value().strip()
    if not raw_value:
        return None

    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw_value, fmt)
        except ValueError:
            continue

    return None


def _normalize_leave_window(from_input, from_date, to_date):
    """Keep generated window aligned with modal baseline date.

    Args:
        from_input: Locator for From date input.
        from_date: Candidate From date.
        to_date: Candidate To date.
    """
    baseline = _parse_prefilled_date(from_input)
    if baseline and from_date.date() < baseline.date():
        shift_days = (baseline.date() - from_date.date()).days
        from_date = from_date + timedelta(days=shift_days)
        to_date = to_date + timedelta(days=shift_days)

    if to_date.date() <= from_date.date():
        to_date = from_date + timedelta(days=1)

    return from_date, to_date


@retry(max_retries=5, delay=0, exceptions=(RuntimeError, PlaywrightTimeoutError))
def _submit_leave_request_attempt(page):
    """Try once to fill and submit a leave request.

    Args:
        page: Active Playwright page.
    """
    leave_page = LeavePage(page)

    from_input = leave_page.dialog.locator("#from_date").first

    start_offset, end_offset = _build_random_leave_window()
    from_date = _date(start_offset)
    to_date = _date(end_offset)
    from_date, to_date = _normalize_leave_window(from_input, from_date, to_date)

    leave_page.fill_leave_details("Annual Leave", None, from_date, to_date)
    leave_page.handle_repeated_alerts(attempts=5)

    leave_page.submit_request()

    try:
        page.wait_for_url("**/pendingleaves")
        return

    except PlaywrightTimeoutError:
        error = page.locator("#errors-from_date")

        if error.count() > 0:
            error_text = error.first.inner_text().strip()
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

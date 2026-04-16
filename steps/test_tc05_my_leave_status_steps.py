"""BDD steps for verifying status of an applied leave."""

from datetime import datetime, timedelta

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect
from pytest_bdd import scenarios, then, when

import steps.test_shared_steps  # noqa: F401
from pages.leave_page import LeavePage
from utils.retry import retry
from utils.test_data_factory import TestDataFactory

scenarios("../features/tc05_my_leave_status.feature")

def _build_random_leave_window():
    """Generate a random valid leave date window."""
    factory = TestDataFactory(seed=None)
    return factory.leave_date_offsets(min_start=5, max_start=120, min_duration=1, max_duration=2)

def _date(offset):
    """Return datetime shifted by day offset.

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
def _submit_leave_request_attempt(page, leave_ctx):
    """Try once to fill and submit a leave request for status validation.

    Args:
        page: Active Playwright page.
        leave_ctx: Mutable fixture used to store leave data for later checks.
    """
    leave_page = LeavePage(page)
    from_input = leave_page.dialog.locator("#from_date").first

    start_offset, end_offset = _build_random_leave_window()
    from_date = _date(start_offset)
    to_date = _date(end_offset)
    from_date, to_date = _normalize_leave_window(from_input, from_date, to_date)

    leave_ctx["leave_type"] = "Emergency Leave"
    leave_ctx["from_date"] = from_date.strftime("%Y/%m/%d")
    leave_ctx["to_date"] = to_date.strftime("%Y/%m/%d")

    leave_ctx["reason"] = leave_page.fill_leave_details("Emergency Leave", None, from_date, to_date)
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
    page.wait_for_url("**/index.php/pendingleaves")

    grid = page.locator("#pendingleaves").first
    grid.wait_for(state="visible")

    rows = grid.locator("tbody tr")
    row_count = rows.count()
    reason_prefix = leave_ctx["reason"][:20].strip()

    target_row = None
    for i in range(row_count):
        row = rows.nth(i)
        leave_type = row.locator("td").nth(1).inner_text().strip()
        row_from = row.locator("td").nth(3).inner_text().strip()
        row_to = row.locator("td").nth(4).inner_text().strip()
        row_text = row.inner_text()

        if (
            leave_type == leave_ctx["leave_type"]
            and row_from == leave_ctx["from_date"]
            and row_to == leave_ctx["to_date"]
            and reason_prefix in row_text
        ):
            target_row = row
            break

    assert target_row is not None, (
        "Applied leave row not found with expected type/date/reason prefix: "
        f"type={leave_ctx['leave_type']}, from={leave_ctx['from_date']}, to={leave_ctx['to_date']}, "
        f"reason_prefix={reason_prefix}"
    )

    status_cell = target_row.locator("td").nth(6)
    expect(status_cell).to_contain_text("Pending for approval")

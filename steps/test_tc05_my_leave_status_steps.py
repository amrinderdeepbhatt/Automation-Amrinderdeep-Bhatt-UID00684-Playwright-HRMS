"""BDD steps for verifying status of an applied leave."""

from datetime import datetime, timedelta
from pathlib import Path

import yaml
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pytest_bdd import scenarios, then, when
from utils.test_data_factory import TestDataFactory
from utils.logger import get_logger

import steps.test_shared_steps  # noqa: F401

scenarios("../features/tc05_my_leave_status.feature")

logger = get_logger()

def _leave_dialog(page):
    """Return the leave request dialog locator."""
    return page.locator("#leaverequestform").first


def _click_ok_if_alert_visible(page, timeout_ms=1000):
    """Dismiss popup alert when visible."""
    ok_button = page.locator("#popup_ok").first
    try:
        ok_button.wait_for(state="visible", timeout=timeout_ms)
    except PlaywrightTimeoutError:
        return False

    ok_button.click()
    return True


def _handle_repeated_alerts(page, attempts=5):
    """Clear repeat alerts that can block form actions."""
    for _ in range(attempts):
        clicked = _click_ok_if_alert_visible(page, timeout_ms=3000)
        if not clicked:
            break
        page.wait_for_timeout(500)

def _build_random_leave_window():
    """Generate a random valid leave date window."""
    factory = TestDataFactory(seed=None)
    return factory.leave_date_offsets(min_start=5, max_start=365, min_duration=1, max_duration=2)

def _load_leave_data():
    """Load valid leave payload from test data."""
    data_path = Path("data/leave.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid_leave"]

def _date(offset):
    """Return datetime shifted by day offset."""
    return datetime.now() + timedelta(days=offset)


def _pick_date_from_calendar(page, input_locator, target_date, min_day=None):
    """Pick a date from datepicker while honoring optional minimum day."""
    input_locator.click()

    datepicker = page.locator("#ui-datepicker-div").first
    datepicker.wait_for(state="visible", timeout=10000)

    for _ in range(12):
        month_text = datepicker.locator(".ui-datepicker-month").first.inner_text().strip()
        year_text = datepicker.locator(".ui-datepicker-year").first.inner_text().strip()

        expected_month = target_date.strftime("%B")
        expected_year = target_date.strftime("%Y")
        if month_text == expected_month and year_text == expected_year:
            break

        datepicker.locator(".ui-datepicker-next").click()

    day = str(target_date.day)
    target_day = datepicker.locator(
        f"xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a[normalize-space()='{day}']"
    ).first

    if target_day.count() and (min_day is None or int(day) > min_day):
        target_day.click()
        return int(day)

    selectable_days = datepicker.locator(
        "xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a"
    )
    total = selectable_days.count()
    if total == 0:
        raise AssertionError("No selectable days available in datepicker")

    chosen_index = 0
    found_greater_day = False
    if min_day is not None:
        for idx in range(total):
            value = int(selectable_days.nth(idx).inner_text().strip())
            if value > min_day:
                chosen_index = idx
                found_greater_day = True
                break

        if not found_greater_day:
            datepicker.locator(".ui-datepicker-next").click()
            selectable_days = datepicker.locator(
                "xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a"
            )
            total = selectable_days.count()
            if total == 0:
                raise AssertionError("No selectable days available in next month datepicker")
            chosen_index = 0

    chosen_day = int(selectable_days.nth(chosen_index).inner_text().strip())
    selectable_days.nth(chosen_index).click()
    return chosen_day


@when("user opens create leave request modal for status validation")
def open_leave_modal_for_status(page):
    """Open create leave request modal for status validation flow."""
    page.locator("td.fc-day.fc-future:visible").first.click()


@when("user handles leave balance warning for status validation if shown")
def handle_warning_for_status(page):
    """Handle leave balance warning popup when it appears."""
    _click_ok_if_alert_visible(page)


@when("user enters valid leave details for status validation")
def enter_leave_details_for_status(page, leave_ctx):
    leave = _load_leave_data()
    dialog = _leave_dialog(page)
    leave_ctx["reason"] = leave["reason"]
    max_attempts = 5
    for attempt in range(max_attempts):
        logger.info(f"Attept {attempt+1} to apply leave for status validation")
        native_leave_type = dialog.locator("#leavetypeid").first
        if native_leave_type.count():
            native_leave_type.select_option(label="Emergency Leave")
        else:
            leave_type = dialog.locator("#s2id_leavetypeid").first
            leave_type.click()
            dropdown = page.locator("#select2-drop").first
            dropdown.wait_for(state="visible", timeout=10000)
            sick_option = dropdown.locator(".select2-results .select2-result-label span", has_text="Sick Leave").first
            if sick_option.count():
                sick_option.click()
            else:
                dropdown.locator(".select2-results .select2-result-selectable").nth(1).click()

        reason_input = dialog.locator("#reason").first
        if reason_input.count():
            reason_input.fill(leave["reason"])

        from_input = dialog.locator("#from_date").first
        to_input = dialog.locator("#to_date").first

        start_offset, end_offset = _build_random_leave_window()
        from_date = _date(start_offset)
        to_date = _date(end_offset)

        selected_from_day = _pick_date_from_calendar(page, from_input, from_date)
        _pick_date_from_calendar(page, to_input, to_date, min_day=selected_from_day)
        _handle_repeated_alerts(page, attempts=5)

        dialog.locator("#submitbutton").click()

        try:
            page.wait_for_url("**/pendingleaves", timeout=5000)
            logger.info("Leave applied and navigated to pending leaves page")
            break

        except PlaywrightTimeoutError:
            error = page.locator("#errors-from_date")

            if error.count() > 0:
                error_text = error.first.inner_text().strip()
                logger.warning(f"Error text: {error_text}")
                if "already been applied" in error_text.lower():
                    continue
                logger.error(f"Unexpected error: {error_text}")
                raise AssertionError(f"Unexpected error: {error_text}")

        break
    else:
        logger.error("Failed to find valid leave date after multiple attempts")
        raise AssertionError("Failed to find a valid leave date range after multiple attempts.")

@then("the applied leave should appear in My Leave with status Pending for approval")
def verify_leave_status(page, leave_ctx):
    """Verify the applied leave appears with pending approval status."""
    page.wait_for_url("**/index.php/pendingleaves")

    grid = page.locator("#pendingleaves").first
    grid.wait_for(state="visible", timeout=10000)

    target_row = grid.locator("tr", has_text=leave_ctx["reason"]).first
    target_row.wait_for(state="visible", timeout=15000)

    status_cell = target_row.locator("td").nth(6)
    try:
        assert "Pending for approval" in status_cell.inner_text().strip()
        logger.info("Leave appears in My leave with Pending for approval status")
    except AssertionError as e:
        logger.error(f"Expected leave status not found: {str(e)}")
        raise
    
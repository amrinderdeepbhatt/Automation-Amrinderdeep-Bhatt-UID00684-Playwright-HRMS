"""BDD steps for validating invalid leave date ranges."""

from datetime import datetime, timedelta

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pytest_bdd import parsers, scenarios, then, when
from utils.logger import get_logger

import steps.test_shared_steps  # noqa: F401

scenarios("../features/tc04_leave_invalid_dates.feature")

logger = get_logger()

def _leave_dialog(page):
    """Return the leave request form locator."""
    return page.locator("#leaverequestform").first


def _click_ok_if_alert_visible(page, timeout_ms=1000):
    """Dismiss alert popup when it is visible."""
    ok_button = page.locator("#popup_ok").first
    try:
        ok_button.wait_for(state="visible", timeout=timeout_ms)
    except PlaywrightTimeoutError:
        return False

    ok_button.click()
    return True


def _pick_date_from_calendar(page, input_locator, target_date):
    """Pick a date from the datepicker, with fallback selection."""
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

    if target_day.count():
        target_day.click()
        return int(day)

    fallback = datepicker.locator(
        "xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a"
    ).first
    chosen_day = int(fallback.inner_text().strip())
    fallback.click()
    return chosen_day


def _pick_date_less_than(page, input_locator, target_date, max_day):
    """Pick a date strictly less than the provided day value."""
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

    selectable_days = datepicker.locator(
        "xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a"
    )
    total = selectable_days.count()
    if total == 0:
        raise AssertionError("No selectable days available in datepicker")

    candidate_index = -1
    candidate_value = -1
    for idx in range(total):
        value = int(selectable_days.nth(idx).inner_text().strip())
        if value < max_day and value > candidate_value:
            candidate_value = value
            candidate_index = idx

    if candidate_index == -1:
        datepicker.locator(".ui-datepicker-prev").click()
        selectable_days = datepicker.locator(
            "xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a"
        )
        total = selectable_days.count()
        if total == 0:
            raise AssertionError("No selectable days available in previous month datepicker")
        selectable_days.nth(total - 1).click()
        return

    selectable_days.nth(candidate_index).click()


def _select_leave_type_for_invalid_validation(page):
    """Select leave type for invalid date validation flow."""
    dialog = _leave_dialog(page)
    native_leave_type = dialog.locator("#leavetypeid").first
    if native_leave_type.count():
        native_leave_type.select_option(label="Annual Leave")
    else:
        dialog.locator("#s2id_leavetypeid").first.click()
        dropdown = page.locator("#select2-drop").first
        dropdown.wait_for(state="visible", timeout=10000)
        dropdown.locator(".select2-results .select2-result-label span", has_text="Annual Leave").first.click()

    dialog.locator("#reason").first.fill("Invalid range validation")


@when("user opens create leave request modal from Apply Leave")
def open_leave_modal(page):
    """Open the leave modal for invalid date checks."""
    logger.info("Opening create leave request modal")
    page.locator("td.fc-day.fc-future:visible").first.click()
    _leave_dialog(page).wait_for(state="visible", timeout=10000)


@when("user handles leave balance warning if shown")
def handle_warning(page):
    """Handle balance warning popup if shown."""
    logger.info("Handling leave balance warning if shown")
    _click_ok_if_alert_visible(page, timeout_ms=3000)


@when("user selects leave type for invalid date validation")
def select_leave_type_for_invalid_dates(page):
    """Select leave type and reason for invalid date validation."""
    logger.info("Selecting leave type for invalid date validation")
    _select_leave_type_for_invalid_validation(page)


@when(parsers.parse("user enters leave dates with from offset {from_offset:d} and to offset {to_offset:d}"))
def fill_invalid_dates(page, from_offset, to_offset):
    """Fill from/to dates using parameterized offsets for validation checks."""
    logger.info(f"Entering leave dates with offsets from={from_offset}, to={to_offset}")
    from_date = datetime.now() + timedelta(days=from_offset)
    to_date = datetime.now() + timedelta(days=to_offset)

    from_input = _leave_dialog(page).locator("#from_date").first
    to_input = _leave_dialog(page).locator("#to_date").first

    selected_from_day = _pick_date_from_calendar(page, from_input, from_date)
    _pick_date_less_than(page, to_input, to_date, max_day=selected_from_day)


@when("user submits leave request with invalid date range")
def submit_invalid_form(page):
    """Submit the leave form with invalid dates."""
    logger.info("Submitting leavae request with invalid range")
    _leave_dialog(page).locator("#submitbutton").click()


@then("user should see invalid to-date validation error")
def verify_to_date_error(page):
    """Assert the expected to-date validation error appears."""
    logger.info("Verifying date error")
    error = page.locator("#errors-to_date").first
    error.wait_for(state="visible", timeout=10000)
    try:
        assert "To date should be greater than from date." in error.inner_text().strip()
        logger.info("Validation error for invalid to-date displayed")
    except AssertionError as e:
        logger.error(f"Expected validation error not found {str(e)}")
        raise

from datetime import datetime, timedelta
from pathlib import Path

import yaml
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pytest_bdd import given, scenarios, then, when
from pages.base_page import BasePage
from utils.logger import get_logger
from utils.test_context import context

scenarios("../features/tc04_leave_invalid_dates.feature")

logger = get_logger()

def _load_valid_creds():
    data_path = Path("data/login.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid"]


def _leave_dialog(page):
    return page.locator("#leaverequestform").first


def _click_ok_if_alert_visible(page, timeout_ms=1000):
    ok_button = page.locator("#popup_ok").first
    try:
        ok_button.wait_for(state="visible", timeout=timeout_ms)
    except PlaywrightTimeoutError:
        return False

    ok_button.click()
    return True


def _pick_date_from_calendar(page, input_locator, target_date):
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
        datepicker.wait_for_timeout(200)
        selectable_days = datepicker.locator(
            "xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a"
        )
        total = selectable_days.count()
        if total == 0:
            raise AssertionError("No selectable days available in previous month datepicker")
        selectable_days.nth(total - 1).click()
        return

    selectable_days.nth(candidate_index).click()


@given("user logs into HRMS and opens Leave Request page for invalid date validation")

def open_leave_page(page, config):
    creds = _load_valid_creds()
    context.page = page
    base_page = BasePage(page)
    logger.info("Logging in and navigating to Leave request page")
    base_page.login(config.get_url(), creds["username"], creds["password"])
    base_page.navigate_to_leave_request()
    
@when("user opens create leave request modal for invalid date validation")
def open_leave_modal(page):
    logger.info("Opening create leave request modal")
    page.locator("td.fc-day.fc-future:visible").first.click()
    _leave_dialog(page).wait_for(state="visible", timeout=10000)


@when("user handles leave balance warning for invalid date validation if shown")
def handle_warning(page):
    logger.info("Handling leave balance warning if shown")
    _click_ok_if_alert_visible(page, timeout_ms=3000)


@when("user selects leave type and enters invalid date range where to date is less than from date")
def fill_invalid_dates(page):
    logger.info("Selecting leave type and invalid date range")
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

    from_date = datetime.now() + timedelta(days=12)
    to_date = datetime.now() + timedelta(days=5)

    from_input = dialog.locator("#from_date").first
    to_input = dialog.locator("#to_date").first

    selected_from_day = _pick_date_from_calendar(page, from_input, from_date)
    _pick_date_less_than(page, to_input, to_date, max_day=selected_from_day)


@when("user submits leave request with invalid date range")
def submit_invalid_form(page):
    logger.info("Submitting leavae request with invalid range")
    _leave_dialog(page).locator("#submitbutton").click()


@then("user should see invalid to-date validation error")
def verify_to_date_error(page):
    logger.info("Verifying date error")
    error = page.locator("#errors-to_date").first
    error.wait_for(state="visible", timeout=10000)
    try:
        assert "To date should be greater than from date." in error.inner_text().strip()
        logger.info("Validation error for invalid to-date displayed")
    except AssertionError as e:
        logger.error(f"Expected validation error not found {str(e)}")
        raise

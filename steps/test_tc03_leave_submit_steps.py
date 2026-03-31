from datetime import datetime, timedelta
from pathlib import Path

import yaml
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pytest_bdd import given, scenarios, then, when
from utils.test_data_factory import TestDataFactory
from pages.base_page import BasePage

from utils.logger import get_logger
from utils.test_context import context

logger = get_logger()

scenarios("../features/tc03_leave_submit.feature")


def _load_valid_creds():
    data_path = Path("data/login.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid"]


def _load_leave_data():
    data_path = Path("data/leave.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid_leave"]


def _build_random_leave_window():
    factory = TestDataFactory(seed=None)
    return factory.leave_date_offsets(min_start=5, max_start=365, min_duration=1, max_duration=5)


def _date(offset):
    return datetime.now() + timedelta(days=offset)


def _pick_date_from_calendar(page, input_locator, target_date, min_day=None):
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
            datepicker.wait_for_timeout(200)
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


def _handle_repeated_alerts(page, attempts=3):
    for _ in range(attempts):
        clicked = _click_ok_if_alert_visible(page, timeout_ms=3000)
        if not clicked:
            break
        page.wait_for_timeout(500)


@given("user logs into HRMS and opens Leave Request page")

def user_on_leave_request(page, config):
    creds = _load_valid_creds()
    context.page = page
    base_page = BasePage(page)
    logger.info("Logging into HRMS and opening leave request page")
    base_page.login(config.get_url(), creds["username"], creds["password"])
    base_page.navigate_to_leave_request()


@when("user opens create leave request modal from Apply Leave")
def open_leave_modal(page):
    logger.info("Opening create leave request modal")
    page.locator("td.fc-day.fc-future:visible").first.click()
    _leave_dialog(page).wait_for(state="visible", timeout=10000)


@when("user handles leave balance warning if shown")
def handle_first_warning(page):
    logger.info("Handling leave balance warning if shown")
    _click_ok_if_alert_visible(page)


@when("user enters leave details with valid date range and submits form")
def fill_leave_form(page):
    leave = _load_leave_data()
    dialog = _leave_dialog(page)
    max_attempts = 5
    logger.info("Filling leave form with valid date range and submitting")
    for attempt in range(max_attempts):
        native_leave_type = dialog.locator("#leavetypeid").first
        if native_leave_type.count():
            native_leave_type.select_option(label="Annual Leave")
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
            break

        except PlaywrightTimeoutError:
            error = page.locator("#errors-from_date")

            if error.count() > 0:
                error_text = error.first.inner_text().strip()
                logger.warning(f"Error text: {error_text}")
                if "already been applied" in error_text.lower():
                    logger.warning("Leave already applied for this date, trying for new date")
                    continue

                raise AssertionError(f"Unexpected error: {error_text}")

        break
    else:
        logger.error("Failed to find a valid leave date range after multiple attempts")
        raise AssertionError("Failed to find a valid leave date range after multiple attempts.")


@then("leave request should be submitted successfully")
def verify_leave_request_submitted(page):
    logger.info("Verifying leave request was submitted successfully")
    page.wait_for_url("**/pendingleaves")
    success = page.get_by_text("Leave request added successfully.", exact=False).first
    success.wait_for(state="visible", timeout=10000)
    assert success.is_visible(), "Leave request success message not visible"


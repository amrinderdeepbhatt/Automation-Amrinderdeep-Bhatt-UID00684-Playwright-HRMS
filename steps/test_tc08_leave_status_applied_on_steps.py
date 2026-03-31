import yaml
from pytest_bdd import given, when, then, scenarios
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger
from pages.base_page import BasePage
from utils.test_context import context

scenarios("../features/tc08_leave_status_filter.feature")

logger = get_logger()

def _load_valid_creds():
    data_path = Path("./data/login.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid"]


def _load_leave_data():
    data_path = Path("./data/leave_filter.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["leave_status"]


def _pick_date_from_calendar(page, input_locator, target_date, min_day=None):
    input_locator.click()

    datepicker = page.locator("#ui-datepicker-div:visible").last
    datepicker.wait_for(state="visible", timeout=10000)

    month_dropdown = datepicker.locator("select.ui-datepicker-month").first
    year_dropdown = datepicker.locator("select.ui-datepicker-year").first

    if not month_dropdown.count() or not year_dropdown.count():
        raise AssertionError("Expected month/year dropdowns were not found in datepicker")

    target_month_zero_based = str(target_date.month - 1)
    target_year = str(target_date.year)
    target_day = str(target_date.day)

    if min_day is not None and int(target_day) <= int(min_day):
        raise AssertionError(f"Target day {target_day} must be greater than min_day {min_day}")

    month_dropdown.select_option(value=target_month_zero_based)
    year_dropdown.select_option(value=target_year)

    day_cell = datepicker.locator(
        (
            "xpath=.//td[@data-handler='selectDay' and @data-month='"
            f"{target_month_zero_based}' and @data-year='{target_year}'"
            "]/a[normalize-space()='"
            f"{target_day}'"
            "]"
        )
    ).last

    if not day_cell.count():
        raise AssertionError(
            f"Day {target_day} not found for month {target_month_zero_based} and year {target_year}"
        )

    day_cell.click()
    return int(target_day)


@given("user logs into HRMS and navigates to My Leave page")
def my_leave_page(page, config):
    creds = _load_valid_creds()
    context.page = page
    logger.info("Logging in and navigating to my leave page")
    base_page = BasePage(page)
    page.goto(config.get_url())
    
    base_page.fill("#username", creds["username"])
    base_page.fill("#password", creds["password"])
    page.locator("#loginsubmit").click()

    base_page.click("#main_parent_4")
    base_page.click("text=My Leave")

    page.wait_for_load_state("networkidle")


@when("user clicks on search button")
def click_search_button(page):
    logger.info("Clicking on search button")
    page.locator("input.togglesearch").first.click()


@when("inputs leave status and applied on in column search")
def input_filter_data(page, context):
    logger.info("Inputting leave status and applied on date in column search")
    page.fill("#leavetype", _load_leave_data())

    applied_on = page.locator("#applieddate").first

    context.filter_date = datetime.strptime("2026/03/26", "%Y/%m/%d").date()

    _pick_date_from_calendar(page, applied_on, context.filter_date)

    logger.info(f"Selected date to input: {applied_on.input_value()}")

@then("leaves should be filtered by leave status and applied on date")
def validate_filter(page, context):

    page.wait_for_load_state("networkidle")

    no_data = page.locator("#pendingleaves .no-data").first
    no_data.wait_for(state="visible", timeout=2000)
    if no_data.count() and no_data.inner_text().strip() == "No data found.":
        logger.warning("No data found for the given filter")
        return

    rows = page.locator("#pendingleaves tbody tr")

    try: 
        assert rows.count() > 0, "No rows found after filtering"

        status = _load_leave_data()
        filter_date = context.filter_date

        for i in range(rows.count()):
            row = rows.nth(i)

            leave = row.locator("td:nth-child(7) span").inner_text().strip()
            applied = row.locator("td:nth-child(8) span").inner_text().strip()

            assert leave == status, f"Expected {status}, got {leave}"

            parsed_applied = None
            for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y,%m,%d"):
                try:
                    parsed_applied = datetime.strptime(applied, fmt).date()
                    break
                except ValueError:
                    continue

            assert parsed_applied is not None, (
                f"Unexpected applied date format: {applied}"
            )

            assert parsed_applied == filter_date, (
                f"Expected {filter_date}, got {parsed_applied}"
            )
    except AssertionError as e:
        logger.error(f"Leave status filter assertion failed: {str(e)}")
        raise

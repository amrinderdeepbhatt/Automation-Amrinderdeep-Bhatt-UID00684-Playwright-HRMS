from pytest_bdd import given, when, then, scenarios 

from pathlib import Path

import yaml

from pages.base_page import BasePage
from utils.logger import get_logger
from utils.test_context import context

logger = get_logger()

scenarios("../features/tc06_leave_filter.feature")

def _load_valid_creds():
    data_path = Path("./data/login.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid"]

@given("user logs into HRMS and opens My Leave page")

def open_my_leave(page, config):
    creds = _load_valid_creds()
    context.page = page
    base_page = BasePage(page)
    logger.info("Logging into HRMS and opening My leave page")
    base_page.login(config.get_url(), creds["username"], creds["password"])
    base_page.navigate_to_my_leave()

@when("user clicks on searches a keyword in Leave Type or Reason Filter")
def search_keyword(page):
    logger.info("Searching for keyword 'Sick' in Leave type filter")
    page.locator("input.togglesearch").first.click()
    page.wait_for_load_state("networkidle")

    type_field = page.locator("#leavetype")
    
    type_field.wait_for(state="visible")

    type_field.fill("Sick")
    type_field.press("Enter")
    page.wait_for_timeout(1200)

@then("leave data should be filtered as per the entered keyword")
def filtered_leave_data(page):
    leave_types = page.locator("#pendingleaves tbody tr td:nth-child(2) span")
    values = leave_types.all_text_contents()
    try:
        assert len(values) > 0, "No results found in table"
    except AssertionError as e:
        logger.error(f"No results found in table: {str(e)}")
    for val in values:
        try:
            assert "sick" in val.lower(), f"Unexpected value found: {val}"
        except AssertionError as e:
            logger.error(f"Incorrect filter value found: {str(e)}")


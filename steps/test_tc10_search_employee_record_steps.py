from pathlib import Path 

import yaml

from pytest_bdd import given, when, then, scenarios
from pages.base_page import BasePage
from utils.logger import get_logger

from utils.test_context import context

logger = get_logger()

scenarios("../features/tc10_search_employee_record.feature")

def _load_valid_creds():
    data_path = Path("./data/login.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid"]

def _get_UUID():
    data_path = Path("./data/uuid.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["uuid"]

@given("user is logged into HRMS and navigates to HR section")

def open_hr_section(page, config):
    logger.info("Logging in and navigating to HR section")
    context.page = page
    creds = _load_valid_creds()
    base_page = BasePage(page)
    base_page.page.goto(config.get_url())
    base_page.fill("#username", creds["username"])
    base_page.fill("#password", creds["password"])
    base_page.click("#loginsubmit")
    base_page.page.wait_for_url("**/welcome")
    base_page.click("#main_parent_3")
    base_page.page.wait_for_load_state("networkidle")

@when("user searches for an employee using a valid Employee UID")
def search_employee(page):
    logger.info("Searching employee using UUID")
    
    page.click("#s2id_search_val")

    page.locator("#search_val").select_option("emp_id")

    page.fill("#search_str", _get_UUID())

    page.get_by_role("button", name="Search").click()

    page.wait_for_selector("#employees_search .list-item")

@then("the system should display the matching employee record")
def validate_employee(page):
    try:
        employees = page.locator("#employees_search .list-item")
        count = employees.count()
        assert count > 0, "No employees found"
        found = False
        for i in range(count):
            emp = employees.nth(i)
            uuid_locator = emp.locator("li:has(i.fa-key) span")
            if uuid_locator.count() == 0:
                continue
            uuid_text = uuid_locator.inner_text().strip()
            if uuid_text == _get_UUID():
                found = True
                break
        assert found, f"Employee with UUID: {_get_UUID()} not found"
    except AssertionError as e:
        logger.error(f"Employee not found: {str(e)}")
        raise


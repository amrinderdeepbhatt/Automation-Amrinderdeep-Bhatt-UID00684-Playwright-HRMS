"""BDD steps for searching an employee by UID."""

from pathlib import Path

import yaml

from pytest_bdd import scenarios, then, when
from playwright.sync_api import expect

import steps.test_shared_steps  # noqa: F401

from utils.logger import get_logger
from utils.test_context import context

logger = get_logger()

scenarios("../features/tc10_search_employee_record.feature")

def _get_UUID():
    """Fetch employee UID value from test data."""
    data_path = Path("./data/uuid.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["uuid"]

@when("user selects Employee UID search type")
def select_employee_uid_search_type(page):
    """Select employee UID as the search criterion.

    Args:
        page: Active Playwright page.
    """
    page.click("#s2id_search_val")
    page.locator("#search_val").select_option("emp_id")


@when("user enters a valid Employee UID")
def enter_valid_employee_uid(page):
    """Enter a valid employee UID into the search field.

    Args:
        page: Active Playwright page.
    """
    uid = _get_UUID()
    context.employee_uid = uid
    page.fill("#search_str", uid)


@when("user clicks employee search button")
def click_employee_search_button(page):
    """Click search and wait for employee results.

    Args:
        page: Active Playwright page.
    """
    page.get_by_role("button", name="Search").click()

    page.wait_for_selector("#employees_search .list-item")

@then("the system should display the matching employee record")
def validate_employee(page):
    """Ensure a matching employee record is present in results.

    Args:
        page: Active Playwright page.
    """
    employees = page.locator("#employees_search .list-item")
    count = employees.count()
    assert count > 0, f"Expected at least one employee result, but found {count}"

    found = False
    for i in range(count):
        emp = employees.nth(i)
        uuid_locator = emp.locator("li:has(i.fa-key) span")
        if uuid_locator.count() == 0:
            continue
        uuid_text = uuid_locator.inner_text().strip()
        if uuid_text == getattr(context, "employee_uid", _get_UUID()):
            found = True
            break

    assert found, f"Expected employee with UID {getattr(context, 'employee_uid', _get_UUID())} not found in results"

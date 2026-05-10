"""BDD steps for searching an employee by UID."""

from pathlib import Path

import yaml

from pytest_bdd import scenarios, then, when

import steps.test_shared_steps
from pages.employee_search_page import EmployeeSearchPage

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
    EmployeeSearchPage(page).select_employee_uid_search_type()


@when("user enters a valid Employee UID")
def enter_valid_employee_uid(page):
    """Enter a valid employee UID into the search field.

    Args:
        page: Active Playwright page.
    """
    uid = _get_UUID()
    context.employee_uid = uid
    EmployeeSearchPage(page).enter_employee_uid(uid)


@when("user clicks employee search button")
def click_employee_search_button(page):
    """Click search and wait for employee results.

    Args:
        page: Active Playwright page.
    """
    EmployeeSearchPage(page).search()

@then("the system should display the matching employee record")
def validate_employee(page):
    """Ensure a matching employee record is present in results.

    Args:
        page: Active Playwright page.
    """
    employee_page = EmployeeSearchPage(page)
    count = employee_page.get_employee_result_count()
    assert count > 0, f"Expected at least one employee result, but found {count}"

    uid = getattr(context, "employee_uid", _get_UUID())
    assert employee_page.has_employee_uid(uid), f"Expected employee with UID {uid} not found in results"

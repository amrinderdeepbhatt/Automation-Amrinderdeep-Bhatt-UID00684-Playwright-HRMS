"""BDD steps for filtering leaves by status and applied date."""

from datetime import datetime
from pathlib import Path

import yaml
from pytest_bdd import scenarios, then, when

import steps.test_shared_steps
from pages.leave_page import LeavePage

from utils.logger import get_logger

scenarios("../features/tc08_leave_status_filter.feature")

logger = get_logger()

def _load_leave_data():
    """Load leave status filter value from YAML."""
    data_path = Path("./data/leave_filter.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["leave_status"]


@when("user inputs leave status and applied on in column search")
def input_filter_data(page, context):
    """Populate leave status and applied-on date filters.

    Args:
        page: Active Playwright page.
        context: Shared test context fixture.
    """
    logger.info("Inputting leave status and applied on date in column search")
    context.filter_date = datetime.strptime("2026/03/26", "%Y/%m/%d").date()

    LeavePage(page).filter_by_status_and_applied_date(_load_leave_data(), context.filter_date)

    logger.info("Selected leave status and applied date filters")

@then("leaves should be filtered by leave status and applied on date")
def validate_filter(page, context):
    """Validate each result row matches selected status and date.

    Args:
        page: Active Playwright page.
        context: Shared test context fixture with selected filters.
    """
    status = _load_leave_data()
    filter_date = context.filter_date
    LeavePage(page).validate_status_and_applied_date_filter(status, filter_date)

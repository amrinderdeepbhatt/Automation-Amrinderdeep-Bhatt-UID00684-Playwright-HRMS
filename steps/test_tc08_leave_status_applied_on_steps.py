"""BDD steps for filtering leaves by status and applied date."""

from datetime import datetime
from pathlib import Path

import yaml
from pytest_bdd import scenarios, then, when
from playwright.sync_api import expect

import steps.test_shared_steps  # noqa: F401
from pages.base_page import BasePage

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
    page.fill("#leavetype", _load_leave_data())
    base_page = BasePage(page)

    applied_on = page.locator("#applieddate").first

    context.filter_date = datetime.strptime("2026/03/26", "%Y/%m/%d").date()

    base_page.pick_date_from_calendar(applied_on, context.filter_date)

    logger.info(f"Selected date to input: {applied_on.input_value()}")

@then("leaves should be filtered by leave status and applied on date")
def validate_filter(page, context):
    """Validate each result row matches selected status and date.

    Args:
        page: Active Playwright page.
        context: Shared test context fixture with selected filters.
    """

    page.wait_for_load_state("networkidle")

    no_data = page.locator("#pendingleaves .no-data").first
    no_data.wait_for(state="visible")
    if no_data.count() and no_data.inner_text().strip() == "No data found.":
        logger.warning("No data found for the given filter")
        return

    rows = page.locator("#pendingleaves tbody tr")
    expect(rows.first).to_be_visible()

    status = _load_leave_data()
    filter_date = context.filter_date

    for i in range(rows.count()):
        row = rows.nth(i)

        leave = row.locator("td:nth-child(7) span").inner_text().strip()
        applied = row.locator("td:nth-child(8) span").inner_text().strip()

        expect(leave).to_equal(status)

        parsed_applied = None
        for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y,%m,%d"):
            try:
                parsed_applied = datetime.strptime(applied, fmt).date()
                break
            except ValueError:
                continue

        expect(parsed_applied is not None).to_be(True)

        expect(parsed_applied).to_equal(filter_date)

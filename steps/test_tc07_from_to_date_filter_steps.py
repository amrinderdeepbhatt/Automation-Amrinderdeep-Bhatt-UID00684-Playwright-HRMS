"""BDD steps for filtering leave records by date range."""

from datetime import datetime, timedelta

from pytest_bdd import scenarios, then, when

import steps.test_shared_steps  # noqa: F401
from pages.base_page import BasePage

from utils.logger import get_logger
from utils.test_data_factory import TestDataFactory

logger = get_logger()

scenarios("../features/tc07_from_to_date_filter.feature")

def _date(offset):
    """Return datetime shifted from today by offset days.

    Args:
        offset: Number of days to shift from today.
    """
    return datetime.now() + timedelta(days=offset)

@when("user fills from and to dates for leave filter")
def filter_from_to_date(page, context):
    """Fill from and to date filters using generated valid dates.

    Args:
        page: Active Playwright page.
        context: Shared test context fixture.
    """
    logger.info("Filtering leave records by from and to dates")

    from_input = page.locator("#from_date").first
    to_input = page.locator("#to_date").first
    base_page = BasePage(page)

    from_input.scroll_into_view_if_needed()
    to_input.scroll_into_view_if_needed()
    from_input.wait_for(state="visible", timeout=10000)
    to_input.wait_for(state="visible", timeout=10000)

    factory = TestDataFactory(seed=None)
    start_offset, end_offset = factory.leave_date_offsets(min_start=5, max_start=50, min_duration=1, max_duration=2)
    from_offset = _date(start_offset)
    to_offset = _date(end_offset)

    context.from_date = from_offset
    context.to_date = to_offset

    base_page.pick_date_from_calendar(from_input, from_offset)
    base_page.pick_date_from_calendar(to_input, to_offset, min_date=from_offset)

@then("leave records should be filtered in selected timeframe")
def validate_timeframe(page, context):
    """Assert listed rows fall within the selected timeframe.

    Args:
        page: Active Playwright page.
        context: Shared test context fixture with selected dates.
    """
    from_dates = page.locator("#pendingleaves tbody tr td:nth-child(4) span")
    to_dates = page.locator("#pendingleaves tbody tr td:nth-child(5) span")

    from_values = from_dates.all_text_contents()
    to_values = to_dates.all_text_contents()
    
    assert len(from_values) == len(to_values), f"Mismatch in row counts: {len(from_values)} from dates vs {len(to_values)} to dates"
    
    selected_from = context.from_date.date()
    selected_to = context.to_date.date()

    for date1, date2 in zip(from_values, to_values):
        row_from = datetime.strptime(date1.strip(), "%Y/%m/%d").date()
        row_to = datetime.strptime(date2.strip(), "%Y/%m/%d").date()

        assert row_from >= selected_from, f"Row from date {row_from} is before selected from date {selected_from}"
        assert row_to <= selected_to, f"Row to date {row_to} is after selected to date {selected_to}"
    
    logger.info("Leave records filtered correctly in selected timeframe")
    
"""BDD steps for filtering leave records by keyword."""

from pytest_bdd import parsers, scenarios, then, when

import steps.test_shared_steps
from pages.leave_page import LeavePage

from utils.logger import get_logger
from utils.test_context import context

logger = get_logger()

scenarios("../features/tc06_leave_filter.feature")


@when(parsers.parse("user enters {keyword} in Leave Type filter"))
def search_keyword(page, keyword):
    """Enter keyword in leave type search field.

    Args:
        page: Active Playwright page.
        keyword: Keyword to enter into the leave type filter.
    """
    context.leave_keyword = keyword
    logger.info(f"Entering keyword '{keyword}' in Leave type filter")

    LeavePage(page).filter_by_leave_type_keyword(keyword)

@then("leave data should be filtered as per the entered keyword")
def filtered_leave_data(page):
    """Validate that filtered rows match the keyword.

    Args:
        page: Active Playwright page.
    """
    keyword = getattr(context, "leave_keyword", None)
    assert keyword, "Leave keyword was not stored before validation"
    LeavePage(page).validate_leave_type_keyword_filter(keyword)

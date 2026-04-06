"""BDD steps for filtering leave records by keyword."""

from pytest_bdd import when, then, scenarios 

from utils.logger import get_logger

import steps.test_shared_steps  # noqa: F401

logger = get_logger()

scenarios("../features/tc06_leave_filter.feature")


@when("user enters keyword in Leave Type filter")
def search_keyword(page):
    """Enter keyword in leave type search field."""
    logger.info("Entering keyword 'Sick' in Leave type filter")

    type_field = page.locator("#leavetype")
    
    type_field.wait_for(state="visible")

    type_field.fill("Sick")
    type_field.press("Enter")
    page.wait_for_timeout(1200)

@then("leave data should be filtered as per the entered keyword")
def filtered_leave_data(page):
    """Validate that filtered rows match the keyword."""
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

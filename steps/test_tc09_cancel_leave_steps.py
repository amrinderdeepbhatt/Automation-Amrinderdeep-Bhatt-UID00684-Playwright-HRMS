"""BDD steps for cancelling a pending leave request."""

from pytest_bdd import scenarios, then, when
from playwright.sync_api import expect

import steps.test_shared_steps  # noqa: F401

from utils.logger import get_logger

logger = get_logger()

scenarios("../features/tc09_cancel_leave_request.feature")

@when("user cancels leave")
def cancel_leave(page, context):
    """Cancel the first pending leave found in the table.

    Args:
        page: Active Playwright page.
        context: Shared test context fixture.
    """
    logger.info("Attempting to cancel leave request")
    page.locator("#filter_all").click()
    rows = page.locator("#pendingleaves tbody tr")
    expect(rows.first).to_be_visible()
    context.leave_id = None

    row_count = rows.count()
    logger.info(f"Found {row_count} rows in pending leaves table")
    
    for i in range(row_count):
        row = rows.nth(i)
        status = row.locator("td:nth-child(7) span").inner_text().strip()
        logger.info(f"Row {i} status: {status}")
        
        if status == "Pending for approval":
            cancel_btn = row.locator("a[id^='cancel_leave_']").first
            
            if cancel_btn.count() > 0:
                btn_id = cancel_btn.get_attribute("id")
                leave_id = btn_id.split("_")[-1]
                context.leave_id = leave_id
                logger.info(f"Cancelling leave {leave_id}")
                cancel_btn.click()
                page.locator("#popup_ok").click()
                page.wait_for_load_state("networkidle")
                break

    assert context.leave_id is not None, "No pending leave found to cancel"

@then("cancelled leave appears on top with valid status")
def validate_cancel(page, context):
    """Verify the cancelled leave shows the expected status.

    Args:
        page: Active Playwright page.
        context: Shared test context fixture containing leave id.
    """
    logger.info("Validating cancelled leave appears on top with status 'Cancelled'")
    page.reload()
    page.wait_for_load_state("networkidle")
    
    row = page.locator(f"a[name='{context.leave_id}']").locator("xpath=ancestor::tr")
    row.wait_for(state="visible", timeout=10000)

    status = row.locator("td:nth-child(7) span").inner_text().strip()
    assert status == "Cancel", f"Expected status 'Cancel' but got '{status}'"

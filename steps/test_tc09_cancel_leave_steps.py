"""BDD steps for cancelling a pending leave request."""

from pytest_bdd import scenarios, when, then

from utils.logger import get_logger

import steps.test_shared_steps  # noqa: F401

logger = get_logger()

scenarios("../features/tc09_cancel_leave_request.feature")

@when("user cancels leave")
def cancel_leave(page, context):
    """Cancel the first pending leave found in the table."""
    logger.info("Attempting to cancel leave request")
    
    try:
        page.locator("#filter_all").click()
        rows = page.locator("#pendingleaves tbody tr")
        assert rows.count() > 0, "No leave records found"
        for i in range(rows.count()):
            row = rows.nth(i)
            status = row.locator("td:nth-child(7) span").inner_text().strip()
            if status == "Pending for approval":
                cancel_btn = row.locator("a[id^='cancel_leave_']").first
                btn_id = cancel_btn.get_attribute("id")
                leave_id = btn_id.split("_")[-1]
                context.leave_id = leave_id
                cancel_btn.click()
                page.locator("#popup_ok").click()
                page.wait_for_load_state("networkidle")
                break
        assert context.leave_id, "No pending leave found"
    except AssertionError as e:
        logger.error(f"Cancel leave request failed: {str(e)}")
        raise

@then("cancelled leave appears on top with valid status")
def validate_cancel(page, context):
    """Verify the cancelled leave shows the expected status."""
    logger.info("Validating cancelled leave appears on top with status 'Cancelled'")
    try:

        row = page.locator(f"a[name='{context.leave_id}']").locator("xpath=ancestor::tr")

        status = row.locator("td:nth-child(7) span").inner_text().strip()
        assert status == "Cancel", f"Expected Cancel but got {status}"
    except AssertionError as e:
        logger.error(f"Cancel leave request not validated: {str(e)}")
        raise
    
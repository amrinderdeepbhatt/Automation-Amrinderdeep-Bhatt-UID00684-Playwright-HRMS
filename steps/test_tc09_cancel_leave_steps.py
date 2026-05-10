"""BDD steps for cancelling a pending leave request."""

from pytest_bdd import scenarios, then, when

import steps.test_shared_steps
from pages.leave_page import LeavePage

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
    context.leave_id = LeavePage(page).cancel_first_pending_leave()

@then("cancelled leave appears on top with valid status")
def validate_cancel(page, context):
    """Verify the cancelled leave shows the expected status.

    Args:
        page: Active Playwright page.
        context: Shared test context fixture containing leave id.
    """
    logger.info("Validating cancelled leave appears on top with status 'Cancelled'")
    LeavePage(page).validate_cancelled_leave(context.leave_id)

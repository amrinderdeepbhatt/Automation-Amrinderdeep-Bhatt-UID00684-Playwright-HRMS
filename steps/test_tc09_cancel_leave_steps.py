import yaml

from pytest_bdd import scenarios, given, when, then

from pathlib import Path
from pages.base_page import BasePage

from utils.logger import get_logger
from utils.test_context import context

logger = get_logger()

scenarios("../features/tc09_cancel_leave_request.feature")

def _load_valid_creds():
    data_path = Path("./data/login.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid"] 

@given("user logs into HRMS and navigates to My leave page")

def my_leave_page(page, config):
    creds = _load_valid_creds()
    context.page = page
    base_page = BasePage(page)
    logger.info("Logging into HRMS and navigating to my leave page")
    base_page.login(config.get_url(), creds["username"], creds["password"])
    base_page.navigate_to_my_leave()
    base_page.page.wait_for_load_state("networkidle")

@when("user cancels leave")
def cancel_leave(page, context):
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
    logger.info("Validating cancelled leave appears on top with status 'Cancelled'")
    try:

        row = page.locator(f"a[name='{context.leave_id}']").locator("xpath=ancestor::tr")

        status = row.locator("td:nth-child(7) span").inner_text().strip()
        assert status == "Cancel", f"Expected Cancel but got {status}"
    except AssertionError as e:
        logger.error(f"Cancel leave request not validated: {str(e)}")
        raise
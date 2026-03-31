from pathlib import Path

import yaml
from pytest_bdd import given, scenarios, then, when
from pages.base_page import BasePage
from utils.logger import get_logger
from utils.test_context import context

scenarios("../features/tc02_login_invalid.feature")

logger = get_logger()

def _load_invalid_creds():
    data_path = Path("data/login.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["invalid"]


@given("user opens the HRMS login page for invalid login")

def open_login_page(page, config):
    base_page = BasePage(page)
    context.page = page
    logger.info("Opening HRMS login page for invalid login")
    base_page.page.goto(config.get_url())


@when("user logs in with invalid credentials from test data")
def login_with_invalid_credentials(page):
    creds = _load_invalid_creds()
    base_page = BasePage(page)
    logger.info(f"Logging in with invalid username: {creds['username']}")
    base_page.login(page.url, creds["username"], creds["password"])


@then("user should see invalid login error")
def verify_invalid_login_error(page):
    expected_text = "The username or password you entered is incorrect."
    logger.info("Verifying invalid login error message")
    error = page.locator("#usernameerror").filter(has_text=expected_text).first
    error.wait_for(state="visible", timeout=10000)
    assert error.inner_text().strip() == expected_text, "Invalid login error message not shown"

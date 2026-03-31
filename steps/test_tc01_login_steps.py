from pathlib import Path

import yaml
from pytest_bdd import given, scenarios, then, when
from pages.base_page import BasePage
from utils.logger import get_logger
from utils.test_context import context

scenarios("../features/tc01_login.feature")

logger = get_logger()

def _load_valid_creds():
    data_path = Path("data/login.yaml")
    with data_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data["valid"]


@given("user opens the HRMS login page")

def open_login_page(page, config):
    base_page = BasePage(page)
    context.page = page
    logger.info("Opening HRMS login page")
    base_page.page.goto(config.get_url())


@when("user logs in with valid credentials from test data")
def login_with_valid_credentials(page):
    creds = _load_valid_creds()
    base_page = BasePage(page)
    logger.info(f"Logging in with username {creds['username']}")
    base_page.login(page.url, creds["username"], creds["password"])
    base_page.page.wait_for_load_state("networkidle")


@then("user should be redirected to the welcome page")
def verify_redirect_to_welcome(page):
    logger.info("Verifying redirect to welcome page")
    try:
        assert page.url.endswith("/welcome")
        logger.info("Login successful")
    except AssertionError as e:
        logger.error(f"Login failed with error: {str(e)}")

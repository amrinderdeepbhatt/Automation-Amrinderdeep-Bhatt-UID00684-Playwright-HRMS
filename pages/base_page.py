from utils.logger import get_logger
from utils.retry import retry
from playwright.sync_api import expect

logger = get_logger()


class BasePage:
    def __init__(self, page):
        self.page = page

    @retry(max_retries=3)
    def click(self, locator):
        logger.info(f"Clicking on {locator}")
        expect(self.page.locator(locator)).to_be_visible()
        self.page.locator(locator).click()

    @retry(max_retries=3)
    def fill(self, locator, text):
        logger.info(f"Filling {locator} with {text}")
        expect(self.page.locator(locator)).to_be_visible()
        self.page.locator(locator).fill(text)

    def wait_for_visible(self, locator):
        logger.info(f"Waiting for {locator}")
        expect(self.page.locator(locator)).to_be_visible()

    def screenshot(self, name="failure.png"):
        path = f"artifacts/screenshots/{name}"
        self.page.screenshot(path=path)
        logger.error(f"Screenshot captured: {path}")

    def login(self, url, username, password):
        try:
            self.page.goto(url)
            self.fill("#username", username)
            self.fill("#password", password)
            self.click("#loginsubmit")
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.screenshot("login_failure.png")
            raise

    def navigate_to_my_leave(self):
        try:
            self.click("#main_parent_4")
            self.page.locator("text=My Leave").click()
            self.page.wait_for_load_state("networkidle")
            logger.info("Navigated to My Leave page")
        except Exception as e:
            logger.error(f"Navigation to My Leave failed: {e}")
            self.screenshot("nav_my_leave_failure.png")
            raise

    def navigate_to_leave_request(self):
        try:
            self.click("#main_parent_4")
            self.page.wait_for_load_state("networkidle")
            logger.info("Navigated to Leave request page")
        except Exception as e:
            logger.error(f"Navigation to Leave Request failed: {e}")
            self.screenshot("nav_leave_request_failure.png")
            raise

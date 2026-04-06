"""Reusable Playwright page actions used across BDD steps."""

from utils.logger import get_logger
from utils.retry import retry
from playwright.sync_api import expect

logger = get_logger()


class BasePage:
    """Wrap common UI interactions with logging and retry support."""

    def __init__(self, page):
        """Store the active Playwright page instance."""
        self.page = page

    @retry(max_retries=3)
    def click(self, locator):
        """Click an element after confirming it is visible."""
        self.wait_for_visible(locator)
        self.page.locator(locator).click()

    @retry(max_retries=3)
    def fill(self, locator, text):
        """Fill an input field after visibility check."""
        self.wait_for_visible(locator)
        self.page.locator(locator).fill(text)

    def wait_for_visible(self, locator):
        """Wait until the given locator becomes visible."""
        expect(self.page.locator(locator)).to_be_visible()


"""Page object for leave module navigation/actions."""

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger()


class LeavePage(BasePage):
    """Encapsulate Leave module navigation actions."""

    def navigate_to_my_leave(self):
        """Open the My Leave section from the main menu."""
        try:
            self.click("#main_parent_4")
            self.page.locator("text=My Leave").click()
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.error(f"Navigation to My Leave failed: {e}")
            raise

    def navigate_to_leave_request(self):
        """Open the Leave Request area from the main menu."""
        try:
            self.click("#main_parent_4")
            self.page.wait_for_load_state("networkidle")
            logger.info("Navigated to Leave request page")
        except Exception as e:
            logger.error(f"Navigation to Leave Request failed: {e}")
            raise

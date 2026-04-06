"""Page object for authentication-related actions."""

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger()


class LoginPage(BasePage):
    """Encapsulate login page interactions."""

    def login(self, url, username, password):
        """Perform login flow and wait for page to settle."""
        try:
            self.page.goto(url)
            self.fill("#username", username)
            self.fill("#password", password)
            self.click("#loginsubmit")
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise

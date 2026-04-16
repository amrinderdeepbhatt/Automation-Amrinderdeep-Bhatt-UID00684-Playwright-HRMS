"""Page object for authentication-related actions."""

from pages.base_page import BasePage
from utils.retry import retry


class LoginPage(BasePage):
    """Encapsulate login page interactions."""

    @retry(max_retries=2, delay=1)
    def login(self, url, username, password):
        """Perform login flow and wait for page to settle.

        Args:
            url: Login page URL.
            username: Username to submit.
            password: Password to submit.
        """
        self.page.goto(url)
        self.fill("#username", username)
        self.fill("#password", password)
        self.click("#loginsubmit")
        self.page.wait_for_load_state("networkidle")

"""Page object for authentication-related actions."""

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Encapsulate login page interactions."""

    INVALID_LOGIN_ERROR_SELECTOR = "#usernameerror"

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

    def validate_invalid_login_error(self, error_text):
        """Assert the invalid login message is visible."""
        error = self.page.locator(self.INVALID_LOGIN_ERROR_SELECTOR).filter(has_text=error_text).first
        error.wait_for(state="visible")
        assert error.inner_text().strip() == error_text

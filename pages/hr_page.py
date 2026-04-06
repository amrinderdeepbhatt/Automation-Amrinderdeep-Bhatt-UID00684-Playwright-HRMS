"""Page object for HR module navigation/actions."""

from pages.base_page import BasePage


class HRPage(BasePage):
    """Encapsulate HR section navigation actions."""

    def navigate_to_hr_section(self):
        """Open the HR section from the main menu."""
        self.click("#main_parent_3")
        self.page.wait_for_load_state("networkidle")

"""Employee search page object helpers used by BDD steps."""

from pages.base_page import BasePage


class EmployeeSearchPage(BasePage):
    """Encapsulate employee search interactions and result validation."""

    SEARCH_TYPE_SELECTOR = "#s2id_search_val"
    SEARCH_VALUE_SELECTOR = "#search_val"
    SEARCH_STRING_SELECTOR = "#search_str"
    SEARCH_BUTTON_SELECTOR = "button:has-text('Search')"
    RESULTS_SELECTOR = "#employees_search .list-item"
    RESULT_UUID_SELECTOR = "li:has(i.fa-key) span"

    def select_employee_uid_search_type(self):
        """Select employee UID as the search criterion."""
        self.click(self.SEARCH_TYPE_SELECTOR)
        self.page.locator(self.SEARCH_VALUE_SELECTOR).select_option("emp_id")

    def enter_employee_uid(self, uid):
        """Enter the employee UID into the search field."""
        self.fill(self.SEARCH_STRING_SELECTOR, uid)

    def search(self):
        """Run the employee search and wait for results to render."""
        self.page.get_by_role("button", name="Search").click()
        self.page.wait_for_selector(self.RESULTS_SELECTOR)

    def get_employee_result_count(self):
        """Return the number of employee result cards."""
        return self.page.locator(self.RESULTS_SELECTOR).count()

    def has_employee_uid(self, uid):
        """Check whether the rendered results include the given UID."""
        employees = self.page.locator(self.RESULTS_SELECTOR)
        for i in range(employees.count()):
            emp = employees.nth(i)
            uuid_locator = emp.locator(self.RESULT_UUID_SELECTOR)
            if uuid_locator.count() == 0:
                continue
            if uuid_locator.inner_text().strip() == uid:
                return True
        return False

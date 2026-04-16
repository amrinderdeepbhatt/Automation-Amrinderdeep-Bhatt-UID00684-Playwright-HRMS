"""Leave request page object helpers used by multiple BDD steps."""

from faker import Faker

from pages.base_page import BasePage


class LeavePage:
    """Encapsulate common leave-request dialog interactions."""

    def __init__(self, page):
        """Store the active Playwright page and shared page helpers.

        Args:
            page: Active Playwright page.
        """
        self.page = page
        self.base_page = BasePage(page)
        self.faker = Faker()

    @property
    def dialog(self):
        """Return the leave request dialog locator."""
        return self.page.locator("#leaverequestform").first

    def open_create_leave_request_modal(self):
        """Open the create leave request modal from the calendar."""
        self.page.locator("td.fc-day.fc-future:visible").first.click()
        self.dialog.wait_for(state="visible")
        self.dismiss_popup_if_visible()

    def select_leave_type(self, leave_type_label):
        """Select a leave type from the leave request form.

        Args:
            leave_type_label: Visible label of the leave type to choose.
        """
        native_leave_type = self.dialog.locator("#leavetypeid").first
        if native_leave_type.count():
            native_leave_type.select_option(label=leave_type_label)
            return

        leave_type = self.dialog.locator("#s2id_leavetypeid").first
        leave_type.click()
        dropdown = self.page.locator("#select2-drop").first
        dropdown.wait_for(state="visible")
        option = dropdown.locator(
            ".select2-results .select2-result-label span",
            has_text=leave_type_label,
        ).first
        if option.count():
            option.click()
        else:
            dropdown.locator(".select2-results .select2-result-selectable").nth(1).click()

    def generate_reason(self):
        """Generate a short unique leave reason."""
        return f"Leave request - {self.faker.sentence(nb_words=4).rstrip('.') }"

    def fill_reason(self, reason=None):
        """Fill the request reason field.

        Args:
            reason: Text to enter into the reason field. Generated when omitted.
        """
        if reason is None:
            reason = self.generate_reason()

        reason_input = self.dialog.locator("#reason").first
        if reason_input.count():
            reason_input.fill(reason)

        return reason

    def fill_leave_details(self, leave_type_label, reason, from_date, to_date):
        """Fill the common valid leave request fields.

        Args:
            leave_type_label: Leave type visible label.
            reason: Request reason. Generated when omitted.
            from_date: Start date for leave.
            to_date: End date for leave.
        """
        self.select_leave_type(leave_type_label)
        reason = self.fill_reason(reason)
        self.fill_leave_date_range(from_date, to_date)
        return reason

    def fill_leave_date_range(self, from_date, to_date):
        """Select a valid From/To date range.

        Args:
            from_date: Start date to choose.
            to_date: End date to choose.
        """
        from_input = self.dialog.locator("#from_date").first
        to_input = self.dialog.locator("#to_date").first
        self.base_page._clear_date_input(from_input)
        self.base_page._clear_date_input(to_input)
        self.base_page.pick_date_range(from_input, to_input, from_date, to_date)

    def fill_invalid_leave_date_range(self, from_date, to_date):
        """Select an invalid From/To date range for validation tests.

        Args:
            from_date: Start date to choose.
            to_date: End date to choose.
        """
        from_input = self.dialog.locator("#from_date").first
        to_input = self.dialog.locator("#to_date").first
        self.base_page._clear_date_input(from_input)
        self.base_page._clear_date_input(to_input)
        selected_from_day = self.base_page.pick_date_from_calendar(from_input, from_date)
        self.base_page.pick_date_less_than(to_input, to_date, max_day=selected_from_day)

    def submit_request(self):
        """Submit the leave request form."""
        self.dialog.locator("#submitbutton").click()

    def dismiss_popup_if_visible(self):
        """Dismiss the warning popup if currently visible."""
        ok_button = self.page.locator("#popup_ok").first
        if ok_button.is_visible():
            ok_button.click()

    def handle_repeated_alerts(self, attempts=5):
        """Dismiss repeated popup alerts that can block the form.

        Args:
            attempts: Maximum number of dismiss attempts.
        """
        for _ in range(attempts):
            ok_button = self.page.locator("#popup_ok").first
            if not ok_button.is_visible():
                break
            ok_button.click()

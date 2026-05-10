"""Leave request page object helpers used by multiple BDD steps."""

from datetime import datetime, timedelta

from faker import Faker

from pages.base_page import BasePage


class LeavePage(BasePage):
    """Encapsulate common leave-request dialog interactions."""

    DIALOG_SELECTOR = "#leaverequestform"
    LEAVE_TYPE_NATIVE_SELECTOR = "#leavetypeid"
    LEAVE_TYPE_SELECT2_SELECTOR = "#s2id_leavetypeid"
    SELECT2_DROPDOWN_SELECTOR = "#select2-drop"
    SELECT2_OPTION_SELECTOR = ".select2-results .select2-result-label span"
    SELECT2_SELECTABLE_SELECTOR = ".select2-results .select2-result-selectable"
    REASON_SELECTOR = "#reason"
    FROM_DATE_SELECTOR = "#from_date"
    TO_DATE_SELECTOR = "#to_date"
    SUBMIT_BUTTON_SELECTOR = "#submitbutton"
    POPUP_OK_SELECTOR = "#popup_ok"
    CALENDAR_FUTURE_SELECTOR = "td.fc-day.fc-future"
    FILTER_FROM_DATE_SELECTOR = "#from_date"
    FILTER_TO_DATE_SELECTOR = "#to_date"
    FILTER_LEAVE_TYPE_SELECTOR = "#leavetype"
    FILTER_APPLIED_DATE_SELECTOR = "#applieddate"
    FILTER_ALL_SELECTOR = "#filter_all"
    LEAVE_TABLE_ROWS_SELECTOR = "#pendingleaves tbody tr"
    LEAVE_TABLE_NO_DATA_SELECTOR = "#pendingleaves .no-data"

    def __init__(self, page):
        """Store the active Playwright page and initialize parent.

        Args:
            page: Active Playwright page.
        """
        super().__init__(page)
        self.faker = Faker()

    @property
    def dialog(self):
        """Return the leave request dialog locator."""
        return self.page.locator(self.DIALOG_SELECTOR).first

    def open_create_leave_request_modal(self):
        """Open the create leave request modal from the calendar."""
        self.click(self.CALENDAR_FUTURE_SELECTOR)
        self.dialog.wait_for(state="visible")
        self._dismiss_popup_if_visible()

    def open_leave_filter_search(self):
        """Open the leave grid search row."""
        self.page.locator("input.togglesearch").first.click()
        self.page.wait_for_load_state("networkidle")

    def open_apply_leave_page(self):
        """Navigate to the Apply Leave page from the main menu."""
        self.navigate_main_menu("Self Service")
        self.click_text("Apply Leave")
        self.page.wait_for_load_state("networkidle")

    def open_pending_leaves_page(self):
        """Navigate to the pending leaves page from the main menu."""
        self.navigate_main_menu("Self Service")
        self.click_text("My Leave")
        self.page.wait_for_load_state("networkidle")

    def select_leave_type(self, leave_type_label):
        """Select a leave type from the leave request form.

        Args:
            leave_type_label: Visible label of the leave type to choose.
        """
        native_leave_type = self.dialog.locator(self.LEAVE_TYPE_NATIVE_SELECTOR).first
        if native_leave_type.count():
            native_leave_type.select_option(label=leave_type_label)
            return

        leave_type = self.dialog.locator(self.LEAVE_TYPE_SELECT2_SELECTOR).first
        leave_type.click()
        dropdown = self.page.locator(self.SELECT2_DROPDOWN_SELECTOR).first
        dropdown.wait_for(state="visible")
        option = dropdown.locator(
            self.SELECT2_OPTION_SELECTOR,
            has_text=leave_type_label,
        ).first
        if option.count():
            option.click()
        else:
            dropdown.locator(self.SELECT2_SELECTABLE_SELECTOR).nth(1).click()

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

        if self.dialog.locator(self.REASON_SELECTOR).first.count():
            self.fill(self.REASON_SELECTOR, reason)

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

    def submit_leave_request(self, leave_type_label, reason, from_date, to_date, valid_range=True):
        """Fill the leave request form and submit it.

        Args:
            leave_type_label: Leave type visible label.
            reason: Request reason. Generated when omitted.
            from_date: Start date for leave.
            to_date: End date for leave.
            valid_range: If True, select a valid date range.
        """
        self.select_leave_type(leave_type_label)
        reason = self.fill_reason(reason)
        self.fill_leave_date_range(from_date, to_date, valid_range=valid_range)
        self.submit_leave_form()
        return reason

    def fill_leave_date_range(self, from_date, to_date, valid_range=True):
        """Select a From/To date range (valid or invalid as needed).

        Args:
            from_date: Start date to choose.
            to_date: End date to choose.
            valid_range: If True, select valid date range. If False, select invalid dates.
        """
        from_input = self.dialog.locator(self.FROM_DATE_SELECTOR).first
        to_input = self.dialog.locator(self.TO_DATE_SELECTOR).first
        self._clear_date_input(from_input)
        self._clear_date_input(to_input)

        if valid_range:
            self.pick_date_range(from_input, to_input, from_date, to_date)
        else:
            selected_from_day = self.pick_date_from_calendar(from_input, from_date)
            self.pick_date_less_than(to_input, to_date, max_day=selected_from_day)

    def normalize_leave_window(self, from_input, from_date, to_date):
        """Keep a generated leave window aligned with the current modal baseline.

        Args:
            from_input: Locator for From date input.
            from_date: Candidate From date.
            to_date: Candidate To date.
        """
        raw_value = from_input.input_value().strip()
        baseline = None
        if raw_value:
            try:
                baseline = datetime.strptime(raw_value, "%Y/%m/%d")
            except ValueError:
                baseline = None

        if baseline and from_date.date() < baseline.date():
            shift_days = (baseline.date() - from_date.date()).days
            from_date = from_date + timedelta(days=shift_days)
            to_date = to_date + timedelta(days=shift_days)

        if to_date.date() <= from_date.date():
            to_date = from_date + timedelta(days=1)

        return from_date, to_date

    def filter_by_leave_type_keyword(self, keyword):
        """Filter leave rows by leave type keyword."""
        type_field = self.page.locator(self.FILTER_LEAVE_TYPE_SELECTOR).first
        type_field.wait_for(state="visible")
        type_field.fill(keyword)
        type_field.press("Enter")

    def validate_leave_type_keyword_filter(self, keyword):
        """Assert at least one leave row matches the given leave type keyword."""
        rows = self.page.locator("#pendingleaves tbody tr td:nth-child(2) span").filter(has_text=keyword)
        count = rows.count()
        assert count > 0, f"Expected at least one '{keyword}' leave entry, but found {count}"

    def filter_by_status_and_applied_date(self, status, applied_on):
        """Fill leave status and applied-on date filters."""
        self.fill(self.FILTER_LEAVE_TYPE_SELECTOR, status)
        applied_input = self.page.locator(self.FILTER_APPLIED_DATE_SELECTOR).first
        self.pick_date_from_calendar(applied_input, applied_on)

    def validate_status_and_applied_date_filter(self, status, filter_date):
        """Validate rows match the selected leave status and applied-on date."""
        self.page.wait_for_load_state("networkidle")

        no_data = self.page.locator(self.LEAVE_TABLE_NO_DATA_SELECTOR).first
        no_data.wait_for(state="visible")
        if no_data.count() and no_data.inner_text().strip() == "No data found.":
            return

        rows = self.page.locator(self.LEAVE_TABLE_ROWS_SELECTOR)
        assert rows.first.is_visible(), "Expected at least one filtered row"

        for i in range(rows.count()):
            row = rows.nth(i)
            leave = row.locator("td:nth-child(7) span").inner_text().strip()
            applied = row.locator("td:nth-child(8) span").inner_text().strip()

            assert leave == status, f"Expected leave status '{status}' but got '{leave}'"

            parsed_applied = datetime.strptime(applied, "%Y/%m/%d").date()
            assert parsed_applied == filter_date, (
                f"Expected applied date '{filter_date}' but got '{parsed_applied}'"
            )

    def cancel_first_pending_leave(self, reset_filters=True):
        """Cancel the first pending leave request in the table and return its leave id.

        Args:
            reset_filters: If True, switch the grid back to the full list before searching.
        """
        if reset_filters:
            self.click(self.FILTER_ALL_SELECTOR)

        rows = self.page.locator(self.LEAVE_TABLE_ROWS_SELECTOR)
        row_count = rows.count()
        assert row_count > 0, "Expected at least one leave row"

        for i in range(row_count):
            row = rows.nth(i)
            status = row.locator("td:nth-child(7) span").inner_text().strip()
            if status != "Pending for approval":
                continue

            cancel_btn = row.locator("a[id^='cancel_leave_']").first
            if cancel_btn.count() == 0:
                continue

            btn_id = cancel_btn.get_attribute("id")
            leave_id = btn_id.split("_")[-1]
            cancel_btn.click()
            self.page.locator(self.POPUP_OK_SELECTOR).click()
            self.page.wait_for_load_state("networkidle")
            return leave_id

        raise AssertionError("No pending leave found to cancel")

    def cancel_leave_for_date_range(self, from_date, to_date):
        """Find and cancel a leave request within the selected date range."""
        self.open_pending_leaves_page()
        self.open_leave_filter_search()
        self.fill_filter_date_range(from_date, to_date)
        return self.cancel_first_pending_leave(reset_filters=False)

    def validate_cancelled_leave(self, leave_id):
        """Assert the cancelled leave shows the expected status."""
        self.page.reload()
        self.page.wait_for_load_state("networkidle")

        row = self.page.locator(f"a[name='{leave_id}']").locator("xpath=ancestor::tr")
        row.wait_for(state="visible", timeout=10000)

        status = row.locator("td:nth-child(7) span").inner_text().strip()
        assert status == "Cancel", f"Expected status 'Cancel' but got '{status}'"

    def get_submission_error_text(self):
        """Return the from-date submission error text if it is visible."""
        error = self.page.locator("#errors-from_date")
        if error.count() == 0:
            return None
        error_text = error.first.inner_text().strip()
        return error_text or None

    def get_field_error_text(self, selector):
        """Return the visible text from a field-level validation error."""
        error = self.page.locator(selector)
        if error.count() == 0:
            return None
        error_text = error.first.inner_text().strip()
        return error_text or None

    def submit_leave_form(self):
        """Click the leave request submit button."""
        self._dismiss_popup_if_visible(attempts=5, wait_ms=150)
        self.dialog.locator(self.SUBMIT_BUTTON_SELECTOR).first.click()

    def validate_pending_leave_submission(self, leave_ctx):
        """Validate the submitted leave row matches the stored request details."""
        self.page.wait_for_load_state("networkidle")
        grid = self.page.locator("#pendingleaves").first
        grid.wait_for(state="visible")

        rows = grid.locator("tbody tr")
        reason_prefix = leave_ctx["reason"][:20].strip()

        target_row = None
        for i in range(rows.count()):
            row = rows.nth(i)
            leave_type = row.locator("td").nth(1).inner_text().strip()
            row_from = row.locator("td").nth(3).inner_text().strip()
            row_to = row.locator("td").nth(4).inner_text().strip()
            row_text = row.inner_text()

            if (
                leave_type == leave_ctx["leave_type"]
                and row_from == leave_ctx["from_date"]
                and row_to == leave_ctx["to_date"]
                and reason_prefix in row_text
            ):
                target_row = row
                break

        assert target_row is not None, (
            "Applied leave row not found with expected type/date/reason prefix: "
            f"type={leave_ctx['leave_type']}, from={leave_ctx['from_date']}, to={leave_ctx['to_date']}, "
            f"reason_prefix={reason_prefix}"
        )

        status_cell = target_row.locator("td").nth(6)
        assert "Pending for approval" in status_cell.inner_text()

    def validate_leave_records_in_timeframe(self, from_date, to_date):
        """Assert leave records are filtered within the selected timeframe."""
        from_dates = self.page.locator("#pendingleaves tbody tr td:nth-child(4) span")
        to_dates = self.page.locator("#pendingleaves tbody tr td:nth-child(5) span")

        from_values = from_dates.all_text_contents()
        to_values = to_dates.all_text_contents()
        assert len(from_values) == len(to_values), (
            f"Mismatch in row counts: {len(from_values)} from dates vs {len(to_values)} to dates"
        )

        selected_from = from_date.date()
        selected_to = to_date.date()

        for date1, date2 in zip(from_values, to_values):
            row_from = datetime.strptime(date1.strip(), "%Y/%m/%d").date()
            row_to = datetime.strptime(date2.strip(), "%Y/%m/%d").date()

            assert row_from >= selected_from, f"Row from date {row_from} is before selected from date {selected_from}"
            assert row_to <= selected_to, f"Row to date {row_to} is after selected to date {selected_to}"

    def get_filter_date_inputs(self):
        """Return the leave filter From/To date inputs."""
        return (
            self.page.locator(self.FILTER_FROM_DATE_SELECTOR).first,
            self.page.locator(self.FILTER_TO_DATE_SELECTOR).first,
        )

    def fill_filter_date_range(self, from_date, to_date):
        """Fill the leave grid date filter using calendar selection."""
        from_input, to_input = self.get_filter_date_inputs()
        from_input.scroll_into_view_if_needed()
        to_input.scroll_into_view_if_needed()
        from_input.wait_for(state="visible", timeout=10000)
        to_input.wait_for(state="visible", timeout=10000)

        self.pick_date_from_calendar(from_input, from_date)
        self.pick_date_from_calendar(to_input, to_date, min_date=from_date)

"""Reusable Playwright page actions used across BDD steps."""

from utils.retry import retry


class BasePage:
    """Wrap common UI interactions with lightweight helpers."""

    MAIN_MENU_SELECTOR = "#main_ul li b"
    DATEPICKER_SELECTOR = "#ui-datepicker-div:visible"
    POPUP_OK_SELECTOR = "#popup_ok"
    DATEPICKER_MONTH_SELECTOR = "select.ui-datepicker-month"
    DATEPICKER_YEAR_SELECTOR = "select.ui-datepicker-year"
    DATEPICKER_MONTH_LABEL_SELECTOR = "span.ui-datepicker-month"
    DATEPICKER_YEAR_LABEL_SELECTOR = "span.ui-datepicker-year"
    DATEPICKER_NEXT_SELECTOR = ".ui-datepicker-next"
    DATEPICKER_PREV_SELECTOR = ".ui-datepicker-prev"
    DATEPICKER_DAY_SELECTOR = "td[data-handler='selectDay']"
    DATEPICKER_PREV_MONTH_DAYS_SELECTOR = "td[data-handler='selectDay']:not(.ui-datepicker-other-month) a"

    def __init__(self, page):
        """Store the active Playwright page instance.

        Args:
            page: Active Playwright page.
        """
        self.page = page

    def click(self, locator):
        """Click an element after confirming it is visible.

        Args:
            locator: Selector string for the target element.
        """
        self.wait_for_visible(locator)
        self.page.locator(locator).first.click()

    def click_text(self, text):
        """Click an element matching visible text."""
        self.wait_for_visible(f"text={text}")
        self.page.locator(f"text={text}").first.click()

    def fill(self, locator, text):
        """Fill an input field after visibility check.

        Args:
            locator: Selector string for the input element.
            text: Value to type into the input.
        """
        self.wait_for_visible(locator)
        self.page.locator(locator).first.fill(text)

    def wait_for_visible(self, locator):
        """Wait until the given locator becomes visible.

        Args:
            locator: Selector string for the element to wait for.
        """
        self.page.locator(locator).first.wait_for(state="visible", timeout=5000)

    def navigate_main_menu(self, menu_name):
        """Click a top-level main menu item by visible name.

        Args:
            menu_name: Visible label of the menu item to open.
        """
        menu_item = self.page.locator(self.MAIN_MENU_SELECTOR, has_text=menu_name).first
        menu_item.wait_for(state="visible", timeout=5000)
        menu_item.click()
        self.page.wait_for_load_state("networkidle")

    def pick_date_from_calendar(self, input_locator, target_date, min_date=None):
        """Pick a date from the visible datepicker.

        Args:
            input_locator: Date input locator that opens the datepicker.
            target_date: Date to select.
            min_date: Optional minimum allowed date boundary.
        """
        if min_date is not None and target_date.date() <= min_date.date():
            raise AssertionError(
                f"Target date {target_date.date()} must be after minimum date {min_date.date()}"
            )

        for attempt in range(2):
            input_locator.click()

            datepicker = self.page.locator(self.DATEPICKER_SELECTOR).last
            datepicker.wait_for(state="visible")

            target_month_zero_based = str(target_date.month - 1)
            target_year = str(target_date.year)
            self._align_datepicker_month_year(datepicker, target_date)

            day = str(target_date.day)
            target_day = datepicker.locator(
                (
                    "xpath=.//td[@data-handler='selectDay'"
                    f" and @data-month='{target_month_zero_based}'"
                    f" and @data-year='{target_year}']"
                    f"/a[normalize-space()='{day}']"
                )
            ).first

            if target_day.count():
                target_day.click()
                self._dismiss_popup_if_visible(attempts=5, wait_ms=150)
                if self._has_date_value(input_locator):
                    return int(day)
                continue

            selectable_days = datepicker.locator(
                (
                    "td[data-handler='selectDay']"
                    f"[data-month='{target_month_zero_based}']"
                    f"[data-year='{target_year}'] a"
                )
            )
            total = selectable_days.count()
            if total == 0:
                raise AssertionError("No selectable days available in datepicker")

            min_day = 0
            if min_date and min_date.year == target_date.year and min_date.month == target_date.month:
                min_day = min_date.day

            requested_day = target_date.day
            fallback_index = -1
            first_valid_index = -1

            for idx in range(total):
                value = int(selectable_days.nth(idx).inner_text().strip())
                if value <= min_day:
                    continue
                if first_valid_index == -1:
                    first_valid_index = idx
                if value >= requested_day:
                    fallback_index = idx
                    break

            if fallback_index == -1:
                fallback_index = first_valid_index

            if fallback_index == -1:
                raise AssertionError("No selectable day satisfies requested date constraints")

            chosen_day = int(selectable_days.nth(fallback_index).inner_text().strip())
            selectable_days.nth(fallback_index).click()
            self._dismiss_popup_if_visible(attempts=5, wait_ms=150)
            if self._has_date_value(input_locator):
                return chosen_day

        raise AssertionError("Date selection did not persist in input field after retry")

    def pick_date_range(self, from_input, to_input, from_date, to_date):
        """Pick From/To dates and recover once if UI clears the From value.

        Args:
            from_input: Locator for the From date input.
            to_input: Locator for the To date input.
            from_date: Start date to select.
            to_date: End date to select.
        """
        self._clear_date_input(from_input)
        self._clear_date_input(to_input)
        self._dismiss_popup_if_visible(attempts=5, wait_ms=150)

        self.pick_date_from_calendar(from_input, from_date)
        self._dismiss_popup_if_visible(attempts=5, wait_ms=150)

        self.pick_date_from_calendar(to_input, to_date, min_date=from_date)
        self._dismiss_popup_if_visible(attempts=5, wait_ms=150)

        if not from_input.input_value().strip():
            self.pick_date_from_calendar(from_input, from_date)
            self._dismiss_popup_if_visible(attempts=5, wait_ms=150)

            self.pick_date_from_calendar(to_input, to_date, min_date=from_date)
            self._dismiss_popup_if_visible(attempts=5, wait_ms=150)

        if not from_input.input_value().strip():
            raise AssertionError("From date is empty after range selection retry")

    def pick_date_less_than(self, input_locator, target_date, max_day):
        """Pick a date strictly less than a provided day value.

        Args:
            input_locator: Date input locator that opens the datepicker.
            target_date: Candidate date used to align month/year.
            max_day: Upper bound for selectable day value.
        """
        input_locator.click()

        datepicker = self.page.locator(self.DATEPICKER_SELECTOR).last
        datepicker.wait_for(state="visible")

        target_month_zero_based = str(target_date.month - 1)
        target_year = str(target_date.year)
        self._align_datepicker_month_year(datepicker, target_date)

        selectable_days = datepicker.locator(
            (
                "td[data-handler='selectDay']"
                f"[data-month='{target_month_zero_based}']"
                f"[data-year='{target_year}'] a"
            )
        )
        total = selectable_days.count()
        if total == 0:
            raise AssertionError("No selectable days available in datepicker")

        candidate_index = -1
        candidate_value = -1
        for idx in range(total):
            value = int(selectable_days.nth(idx).inner_text().strip())
            if value < max_day and value > candidate_value:
                candidate_value = value
                candidate_index = idx

        if candidate_index == -1:
            datepicker.locator(self.DATEPICKER_PREV_SELECTOR).click()
            selectable_days = datepicker.locator(self.DATEPICKER_PREV_MONTH_DAYS_SELECTOR)
            total = selectable_days.count()
            if total == 0:
                raise AssertionError("No selectable days available in previous month datepicker")
            selectable_days.nth(total - 1).click()
            return

        selectable_days.nth(candidate_index).click()

    def _align_datepicker_month_year(self, datepicker, target_date):
        """Navigate the open datepicker to the target month/year.

        Args:
            datepicker: Locator for the visible datepicker container.
            target_date: Target date that defines desired month/year.
        """
        target_month_index = target_date.month - 1
        target_year = target_date.year

        if self._is_displayed_month_year_target(datepicker, target_month_index, target_year):
            return

        month_dropdown = datepicker.locator("select.ui-datepicker-month").first
        year_dropdown = datepicker.locator("select.ui-datepicker-year").first

        if month_dropdown.count() and year_dropdown.count():
            target_month_zero_based = str(target_month_index)
            target_year_str = str(target_year)

            if month_dropdown.locator(f"option[value='{target_month_zero_based}']").count():
                if month_dropdown.input_value() != target_month_zero_based:
                    month_dropdown.select_option(value=target_month_zero_based)

            if year_dropdown.locator(f"option[value='{target_year_str}']").count():
                if year_dropdown.input_value() != target_year_str:
                    year_dropdown.select_option(value=target_year_str)

            if self._is_displayed_month_year_target(datepicker, target_month_index, target_year):
                return

        current_month_index, current_year = self._get_displayed_month_year(datepicker)
        nav_selector = (
            self.DATEPICKER_NEXT_SELECTOR
            if (current_year, current_month_index) < (target_year, target_month_index)
            else self.DATEPICKER_PREV_SELECTOR
        )

        for _ in range(24):
            if self._is_displayed_month_year_target(datepicker, target_month_index, target_year):
                return

            nav_button = datepicker.locator(nav_selector).first
            if not nav_button.count():
                break

            classes = nav_button.get_attribute("class") or ""
            if "ui-state-disabled" in classes:
                break

            nav_button.click()

        if not self._is_displayed_month_year_target(datepicker, target_month_index, target_year):
            raise AssertionError(
                f"Unable to open calendar month/year {target_date.strftime('%B')} {target_year}"
            )

    def _is_displayed_month_year_target(self, datepicker, target_month_index, target_year):
        """Check if datepicker is displaying the target month and year.

        Args:
            datepicker: Locator for the visible datepicker container.
            target_month_index: Target zero-based month index (0-11).
            target_year: Target year.
        """
        month_index, year = self._get_displayed_month_year(datepicker)
        return month_index == target_month_index and year == target_year

    def _get_displayed_month_year(self, datepicker):
        """Return currently displayed datepicker month index and year.

        Args:
            datepicker: Locator for the visible datepicker container.
        """
        month_dropdown = datepicker.locator(self.DATEPICKER_MONTH_SELECTOR).first
        year_dropdown = datepicker.locator(self.DATEPICKER_YEAR_SELECTOR).first

        assert month_dropdown.count() and year_dropdown.count(), (
            "Datepicker month/year dropdowns not found"
        )
        return int(month_dropdown.input_value()), int(year_dropdown.input_value())

    def _dismiss_popup_if_visible(self, attempts=3, wait_ms=120):
        """Dismiss optional warning popup, including slightly delayed appearances.

        Args:
            attempts: Number of short re-checks for delayed popup render.
            wait_ms: Delay between checks in milliseconds.
        """
        for _ in range(attempts):
            ok_button = self.page.locator(self.POPUP_OK_SELECTOR).first
            if ok_button.count() and ok_button.is_visible():
                ok_button.click()
                return
            self.page.wait_for_timeout(wait_ms)

    def _has_date_value(self, input_locator):
        """Check whether a date input currently contains a value.

        Args:
            input_locator: Locator for date input field.
        """
        return bool(input_locator.input_value().strip())

    def _clear_date_input(self, input_locator):
        """Clear a readonly date input via script to reset modal defaults.

        Args:
            input_locator: Locator for date input field.
        """
        input_locator.evaluate(
            """
            el => {
                el.value = '';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            """
        )

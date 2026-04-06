"""BDD steps for filtering leave records by date range."""

from pytest_bdd import when, then, scenarios 

from utils.test_data_factory import TestDataFactory

from datetime import datetime, timedelta

from utils.logger import get_logger

import steps.test_shared_steps  # noqa: F401

logger = get_logger()

scenarios("../features/tc07_from_to_date_filter.feature")

def _date(offset):
    """Return datetime shifted from today by offset days."""
    return datetime.now() + timedelta(days=offset)

def _pick_date_from_calendar(page, input_locator, target_date, min_day=None):
    """Pick a date from the datepicker with optional minimum day."""
    input_locator.click()

    datepicker = page.locator("#ui-datepicker-div").first
    datepicker.wait_for(state="visible", timeout=10000)

    for _ in range(12):
        month_text = datepicker.locator(".ui-datepicker-month").first.inner_text().strip()
        year_text = datepicker.locator(".ui-datepicker-year").first.inner_text().strip()

        expected_month = target_date.strftime("%B")
        expected_year = target_date.strftime("%Y")
        if month_text == expected_month and year_text == expected_year:
            break

        datepicker.locator(".ui-datepicker-next").click()

    day = str(target_date.day)
    target_day = datepicker.locator(
        f"xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a[normalize-space()='{day}']"
    ).first

    if target_day.count() and (min_day is None or int(day) > min_day):
        target_day.click()
        return int(day)

    selectable_days = datepicker.locator(
        "xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a"
    )
    total = selectable_days.count()
    if total == 0:
        raise AssertionError("No selectable days available in datepicker")

    chosen_index = 0
    found_greater_day = False
    if min_day is not None:
        for idx in range(total):
            value = int(selectable_days.nth(idx).inner_text().strip())
            if value > min_day:
                chosen_index = idx
                found_greater_day = True
                break

        if not found_greater_day:
            datepicker.locator(".ui-datepicker-next").click()
            datepicker.wait_for_timeout(200)
            selectable_days = datepicker.locator(
                "xpath=.//td[@data-handler='selectDay' and not(contains(@class,'ui-datepicker-other-month'))]/a"
            )
            total = selectable_days.count()
            if total == 0:
                raise AssertionError("No selectable days available in next month datepicker")
            chosen_index = 0

    chosen_day = int(selectable_days.nth(chosen_index).inner_text().strip())
    selectable_days.nth(chosen_index).click()
    return chosen_day

@when("user fills from and to dates for leave filter")
def filter_from_to_date(page, context):
    """Fill from and to date filters using generated valid dates."""
    logger.info("Filtering leave records by from and to dates")

    from_input = page.locator("#from_date").first
    to_input = page.locator("#to_date").first

    factory = TestDataFactory(seed=None)
    start_offset, end_offset = factory.leave_date_offsets(min_start=5, max_start=50, min_duration=1, max_duration=2)
    from_offset = _date(start_offset)
    to_offset = _date(end_offset)

    context.from_date = from_offset
    context.to_date = to_offset

    selected_from_day = _pick_date_from_calendar(page, from_input, from_offset)
    _pick_date_from_calendar(page, to_input, to_offset, min_day=selected_from_day)

@then("leave records should be filtered in selected timeframe")
def validate_timeframe(page, context):
    """Assert listed rows fall within the selected timeframe."""
    from_dates = page.locator("#pendingleaves tbody tr td:nth-child(4) span")
    to_dates = page.locator("#pendingleaves tbody tr td:nth-child(5) span")

    from_values = from_dates.all_text_contents()
    to_values = to_dates.all_text_contents()
    try:
        assert len(from_values) == len(to_values), "Mismatch in count of from and to rows"
        selected_from = context.from_date.date()
        selected_to = context.to_date.date()

        for date1, date2 in zip(from_values, to_values):

            row_from = datetime.strptime(date1.strip(), "%Y/%m/%d").date()
            row_to = datetime.strptime(date2.strip(), "%Y/%m/%d").date()

            assert row_from >= selected_from, (
                f"Row FROM date {row_from} is before selected FROM {selected_from}"
            )

            assert row_to <= selected_to, (
                f"Row TO date {row_to} is after selected TO {selected_to}"
            )
        logger.info("Leave records filtered correctly in selected timeframe")
    except AssertionError as e:
        logger.error(f"Timeframe filter assertion failed: {str(e)}")
        raise
    
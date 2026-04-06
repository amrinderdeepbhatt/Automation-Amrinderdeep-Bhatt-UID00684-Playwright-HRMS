"""Factories for generating realistic dynamic test data."""

from faker import Faker

import random

class TestDataFactory:
    """Build repeatable fake values used by UI tests."""

    __test__ = False

    def __init__(self, seed=random.randint(1000, 9999)):
        """Initialize Faker with a per-instance seed."""
        self.faker = Faker()
        self.faker.seed_instance(seed)

    def employee_uid(self):
        """Return an employee ID in project format."""
        return f"EMP-{self.faker.random_int(min=1000, max=9999)}"

    def keyword(self):
        """Return a short random keyword."""
        return self.faker.word()

    def leave_date_offsets(self, min_start=3, max_start=45, min_duration=1, max_duration=3):
        """Generate start and end offsets for a valid leave window."""
        start_offset = self.faker.random_int(min=min_start, max=max_start)
        duration = self.faker.random_int(min=min_duration, max=max_duration)
        end_offset = start_offset + duration
        return start_offset, end_offset

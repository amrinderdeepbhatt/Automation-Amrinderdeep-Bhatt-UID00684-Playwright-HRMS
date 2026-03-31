from faker import Faker

import random

class TestDataFactory:
    __test__ = False

    def __init__(self, seed=random.randint(1000, 9999)):
        self.faker = Faker()
        self.faker.seed_instance(seed)

    def employee_uid(self):
        return f"EMP-{self.faker.random_int(min=1000, max=9999)}"

    def keyword(self):
        return self.faker.word()

    def leave_reason(self):
        return self.faker.sentence(nb_words=4)

    def leave_date_offsets(self, min_start=3, max_start=45, min_duration=1, max_duration=3):
        start_offset = self.faker.random_int(min=min_start, max=max_start)
        duration = self.faker.random_int(min=min_duration, max=max_duration)
        end_offset = start_offset + duration
        return start_offset, end_offset

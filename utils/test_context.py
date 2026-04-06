"""Shared lightweight context object for passing state between steps."""

class TestContext:
    """Container for mutable runtime test state."""

    page = None

context = TestContext()

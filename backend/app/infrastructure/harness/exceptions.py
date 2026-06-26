class HarnessError(Exception):
    """Base class for harness controlled stops."""


class HarnessBlocked(HarnessError):
    """Raised internally when the harness blocks an action."""


class HarnessLimitExceeded(HarnessBlocked):
    """Raised internally when a run or session limit is exceeded."""


class HarnessTimeout(HarnessBlocked):
    """Raised internally when a request or tool timeout is reached."""

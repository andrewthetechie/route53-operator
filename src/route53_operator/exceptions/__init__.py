class RecordNotFoundError(Exception):
    """Raised when a record is not found in a hosted zone."""

    pass


class InvalidRecordChange(Exception):
    """Raised when a change is invalid"""

    pass

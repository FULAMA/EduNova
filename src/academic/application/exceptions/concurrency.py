class AcademicRecordConcurrencyError(RuntimeError):
    """Raised when a record changed before a conditional write."""

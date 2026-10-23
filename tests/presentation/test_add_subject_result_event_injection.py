from src.academic.application.use_cases.add_subject_result import AddSubjectResult
from src.presentation.api.container import ApplicationContainer
from src.shared.application.events.in_memory_event_dispatcher import (
    InMemoryEventDispatcher,
)
from src.infrastructure.persistence.database import SQLiteDatabase


def test_container_injects_event_dispatcher_into_add_subject_result():
    container = ApplicationContainer(
        database=SQLiteDatabase(":memory:")
    )

    use_case = container.add_subject_result()

    assert isinstance(use_case, AddSubjectResult)
    assert isinstance(
        use_case._event_dispatcher,
        InMemoryEventDispatcher,
    )

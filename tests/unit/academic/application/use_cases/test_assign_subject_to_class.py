from src.academic.application.dto.assign_subject_to_class_request import AssignSubjectToClassRequest
from uuid import uuid4



import pytest



from src.academic.application.interfaces.class_option_repository import (

    ClassOptionRepository,

)

from src.academic.application.use_cases.assign_subject_to_class import (

    AssignSubjectToClass,

)

from src.academic.domain.entities.academic_class import AcademicClass

from src.academic.domain.entities.class_subject import ClassSubject
from src.academic.domain.entities.class_option import ClassOption

from src.academic.domain.entities.subject import Subject
from tests.support.tenant import TEST_TENANT_ID





class FakeClassSubjectRepository:

    def __init__(self):

        self.items = {}



    def save(self, class_subject: ClassSubject) -> None:

        self.items[class_subject.id] = class_subject



    def find_by_class_and_option(

        self,

        academic_class_id,

        academic_option_id,

        tenant_id=None,

    ):

        return [

            item

            for item in self.items.values()

            if (

                item.academic_class_id == academic_class_id

                and item.academic_option_id == academic_option_id

                and (tenant_id is None or item.tenant_id == tenant_id)

            )

        ]





class FakeAcademicClassRepository:

    def __init__(self):

        self.items = {}



    def add(self, academic_class):

        self.items[academic_class.id] = academic_class



    def find_by_id(self, academic_class_id, tenant_id):

        item = self.items.get(academic_class_id)

        if item is None:

            return None

        if item.tenant_id != tenant_id:

            return None

        return item





class FakeSubjectRepository:

    def __init__(self):

        self.items = {}



    def add(self, subject):

        self.items[subject.id] = subject



    def find_by_id(self, subject_id, tenant_id):

        item = self.items.get(subject_id)

        if item is None:

            return None

        if item.tenant_id != tenant_id:

            return None

        return item





class FakeClassOptionRepository(ClassOptionRepository):

    def __init__(self):

        self.items = {}



    def save(self, class_option):

        self.items[class_option.id] = class_option



    def find_by_id(self, class_option_id, tenant_id):

        item = self.items.get(class_option_id)

        if item is None:

            return None

        if item.tenant_id != tenant_id:

            return None

        return item



    def find_by_class_and_option(

        self,

        academic_class_id,

        academic_option_id,

        tenant_id,

    ):

        for item in self.items.values():

            if (

                item.academic_class_id == academic_class_id

                and item.academic_option_id == academic_option_id

                and item.tenant_id == tenant_id

                and item.active

            ):

                return item



        return None





def build_use_case(

    class_repository,

    subject_repository,

    class_subject_repository,

    class_option_repository,

):

    return AssignSubjectToClass(

        academic_class_repository=class_repository,

        subject_repository=subject_repository,

        class_subject_repository=class_subject_repository,

        class_option_repository=class_option_repository,

    )





def test_assign_subject_to_class_creates_class_subject():

    class_id = uuid4()

    subject_id = uuid4()



    academic_class = AcademicClass(

        id=class_id,

        tenant_id=TEST_TENANT_ID,

        name="6e Scientifique",

    )



    subject = Subject(

        id=subject_id,

        tenant_id=TEST_TENANT_ID,

        name="MathÃ©matiques",

        code="MATH",

        coefficient=3,

    )



    class_repository = FakeAcademicClassRepository()

    subject_repository = FakeSubjectRepository()

    class_subject_repository = FakeClassSubjectRepository()

    class_option_repository = FakeClassOptionRepository()



    class_repository.add(academic_class)

    subject_repository.add(subject)



    use_case = build_use_case(

        class_repository,

        subject_repository,

        class_subject_repository,

        class_option_repository,

    )



    result = use_case.execute(
        AssignSubjectToClassRequest(
            tenant_id=TEST_TENANT_ID,
            academic_class_id=class_id,
            subject_id=subject_id,
            coefficient=3,
        )
    )


    assert result.academic_class_id == class_id
    assert result.subject_id == subject_id
    assert result.coefficient == 3
    assert result.academic_option_id is None
    assert result.active is True

    assert result.academic_class_id == class_id

    assert result.subject_id == subject_id

    assert result.coefficient == 3

    assert result.academic_option_id is None



    saved = class_subject_repository.find_by_class_and_option(

        class_id,

        None,

        TEST_TENANT_ID,

    )



    assert len(saved) == 1
    assert saved[0].id == result.id
    assert saved[0].academic_class_id == result.academic_class_id
    assert saved[0].subject_id == result.subject_id
    assert saved[0].coefficient == result.coefficient
    assert saved[0].academic_option_id == result.academic_option_id
    assert saved[0].active == result.active





def test_assign_subject_to_class_fails_if_class_does_not_exist():

    class_repository = FakeAcademicClassRepository()

    subject_repository = FakeSubjectRepository()

    class_subject_repository = FakeClassSubjectRepository()

    class_option_repository = FakeClassOptionRepository()



    use_case = build_use_case(

        class_repository,

        subject_repository,

        class_subject_repository,

        class_option_repository,

    )



    with pytest.raises(

        ValueError,

        match="La classe académique n'existe pas",

    ):

        use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=TEST_TENANT_ID,
                academic_class_id=uuid4(),
                subject_id=uuid4(),
                coefficient=3,
            )
        )




def test_assign_subject_to_class_fails_if_subject_does_not_exist():

    class_id = uuid4()



    academic_class = AcademicClass(

        id=class_id,

        tenant_id=TEST_TENANT_ID,

        name="6e Scientifique",

    )



    class_repository = FakeAcademicClassRepository()

    subject_repository = FakeSubjectRepository()

    class_subject_repository = FakeClassSubjectRepository()

    class_option_repository = FakeClassOptionRepository()



    class_repository.add(academic_class)



    use_case = build_use_case(

        class_repository,

        subject_repository,

        class_subject_repository,

        class_option_repository,

    )



    with pytest.raises(

        ValueError,

        match="La matière n'existe pas",

    ):

        use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=TEST_TENANT_ID,
                academic_class_id=class_id,
                subject_id=uuid4(),
                coefficient=3,
            )
        )




def test_assign_subject_to_class_rejects_non_positive_coefficient():

    class_id = uuid4()

    subject_id = uuid4()



    academic_class = AcademicClass(

        id=class_id,

        tenant_id=TEST_TENANT_ID,

        name="6e Scientifique",

    )



    subject = Subject(

        id=subject_id,

        tenant_id=TEST_TENANT_ID,

        name="MathÃ©matiques",

        code="MATH",

        coefficient=3,

    )



    class_repository = FakeAcademicClassRepository()

    subject_repository = FakeSubjectRepository()

    class_subject_repository = FakeClassSubjectRepository()

    class_option_repository = FakeClassOptionRepository()



    class_repository.add(academic_class)

    subject_repository.add(subject)



    use_case = build_use_case(

        class_repository,

        subject_repository,

        class_subject_repository,

        class_option_repository,

    )



    with pytest.raises(

        ValueError,

        match="Le coefficient doit être supérieur à zéro",

    ):

        use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=TEST_TENANT_ID,
                academic_class_id=class_id,
                subject_id=subject_id,
                coefficient=0,
            )
        )




def test_assign_subject_to_class_rejects_duplicate_subject():

    class_id = uuid4()

    subject_id = uuid4()



    academic_class = AcademicClass(

        id=class_id,

        tenant_id=TEST_TENANT_ID,

        name="6e Scientifique",

    )



    subject = Subject(

        id=subject_id,

        tenant_id=TEST_TENANT_ID,

        name="MathÃ©matiques",

        code="MATH",

        coefficient=3,

    )



    class_repository = FakeAcademicClassRepository()

    subject_repository = FakeSubjectRepository()

    class_subject_repository = FakeClassSubjectRepository()

    class_option_repository = FakeClassOptionRepository()



    class_repository.add(academic_class)

    subject_repository.add(subject)



    existing = ClassSubject(

        id=uuid4(),

        tenant_id=TEST_TENANT_ID,

        academic_class_id=class_id,

        subject_id=subject_id,

        coefficient=3,

    )



    class_subject_repository.save(existing)



    use_case = build_use_case(

        class_repository,

        subject_repository,

        class_subject_repository,

        class_option_repository,

    )



    with pytest.raises(

        ValueError,

        match="La matière est déjà assignée à cette classe",

    ):

        use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=TEST_TENANT_ID,
                academic_class_id=class_id,
                subject_id=subject_id,
                coefficient=3,
            )
        )




def test_assign_subject_to_class_rejects_option_not_belonging_to_class():

    class_id = uuid4()

    subject_id = uuid4()

    option_id = uuid4()



    academic_class = AcademicClass(

        id=class_id,

        tenant_id=TEST_TENANT_ID,

        name="6e Scientifique",

    )



    subject = Subject(

        id=subject_id,

        tenant_id=TEST_TENANT_ID,

        name="MathÃ©matiques",

        code="MATH",

        coefficient=3,

    )



    class_repository = FakeAcademicClassRepository()

    subject_repository = FakeSubjectRepository()

    class_subject_repository = FakeClassSubjectRepository()

    class_option_repository = FakeClassOptionRepository()



    class_repository.add(academic_class)

    subject_repository.add(subject)



    use_case = build_use_case(

        class_repository,

        subject_repository,

        class_subject_repository,

        class_option_repository,

    )



    with pytest.raises(

        ValueError,

        match="L'option académique n'appartient pas à cette classe",

    ):

        use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=TEST_TENANT_ID,
                academic_class_id=class_id,
                subject_id=subject_id,
                coefficient=3,
                academic_option_id=option_id,
            )
        )

def test_assign_subject_to_class_accepts_valid_option():

    class_id = uuid4()

    subject_id = uuid4()

    option_id = uuid4()



    academic_class = AcademicClass(

        id=class_id,

        tenant_id=TEST_TENANT_ID,

        name="6e Scientifique",

    )



    subject = Subject(

        id=subject_id,

        tenant_id=TEST_TENANT_ID,

        name="Programmation",

        code="PROG",

        coefficient=4,

    )



    class_option = ClassOption(

        id=uuid4(),

        tenant_id=TEST_TENANT_ID,

        academic_class_id=class_id,

        academic_option_id=option_id,

    )



    class_repository = FakeAcademicClassRepository()

    subject_repository = FakeSubjectRepository()

    class_subject_repository = FakeClassSubjectRepository()

    class_option_repository = FakeClassOptionRepository()



    class_repository.add(academic_class)

    subject_repository.add(subject)

    class_option_repository.save(class_option)



    use_case = build_use_case(

        class_repository,

        subject_repository,

        class_subject_repository,

        class_option_repository,

    )



    result = use_case.execute(
        AssignSubjectToClassRequest(
            tenant_id=TEST_TENANT_ID,
            academic_class_id=class_id,
            subject_id=subject_id,
            coefficient=4,
            academic_option_id=option_id,
        )
    )


    assert result.academic_class_id == class_id
    assert result.subject_id == subject_id
    assert result.coefficient == 4
    assert result.academic_option_id == option_id
    assert result.active is True

    assert result.academic_class_id == class_id

    assert result.subject_id == subject_id

    assert result.academic_option_id == option_id

    assert result.coefficient == 4






def test_assign_subject_to_class_rejects_inactive_option():

    class_id = uuid4()

    subject_id = uuid4()

    option_id = uuid4()



    academic_class = AcademicClass(

        id=class_id,

        tenant_id=TEST_TENANT_ID,

        name="6e Scientifique",

    )



    subject = Subject(

        id=subject_id,

        tenant_id=TEST_TENANT_ID,

        name="Programmation",

        code="PROG",

        coefficient=4,

    )



    inactive_class_option = ClassOption(

        id=uuid4(),

        tenant_id=TEST_TENANT_ID,

        academic_class_id=class_id,

        academic_option_id=option_id,

        active=False,

    )



    class_repository = FakeAcademicClassRepository()

    subject_repository = FakeSubjectRepository()

    class_subject_repository = FakeClassSubjectRepository()

    class_option_repository = FakeClassOptionRepository()



    class_repository.add(academic_class)

    subject_repository.add(subject)

    class_option_repository.save(inactive_class_option)



    use_case = build_use_case(

        class_repository,

        subject_repository,

        class_subject_repository,

        class_option_repository,

    )



    with pytest.raises(

        ValueError,

        match="L'option académique n'appartient pas à cette classe",

    ):

        use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=TEST_TENANT_ID,
                academic_class_id=class_id,
                subject_id=subject_id,
                coefficient=4,
                academic_option_id=option_id,
            )
        )

def test_assign_subject_to_class_rejects_class_and_subject_from_different_tenants():
    tenant_a = TEST_TENANT_ID
    tenant_b = uuid4()

    class_id = uuid4()
    subject_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        tenant_id=tenant_a,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        tenant_id=tenant_b,
        name="MathÃ©matiques",
        code="MATH",
        coefficient=3,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    with pytest.raises(
        ValueError,
        match="La matière n'existe pas",
    ):
        use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=tenant_a,
                academic_class_id=class_id,
                subject_id=subject_id,
                coefficient=3,
            )
        )

def test_assign_subject_to_class_rejects_option_from_different_tenant():
    tenant_a = TEST_TENANT_ID
    tenant_b = uuid4()

    class_id = uuid4()
    subject_id = uuid4()
    option_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        tenant_id=tenant_a,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        tenant_id=tenant_a,
        name="MathÃ©matiques",
        code="MATH",
        coefficient=3,
    )

    class_option = ClassOption(
        id=uuid4(),
        tenant_id=tenant_b,
        academic_class_id=class_id,
        academic_option_id=option_id,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)
    class_option_repository.save(class_option)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    with pytest.raises(
        ValueError,
        match="L'option académique n'appartient pas à cette classe",
    ):
        use_case.execute(
            AssignSubjectToClassRequest(
                tenant_id=tenant_a,
                academic_class_id=class_id,
                subject_id=subject_id,
                coefficient=3,
                academic_option_id=option_id,
            )
        )


def test_assign_subject_to_class_does_not_consider_other_tenant_duplicate():
    tenant_a = TEST_TENANT_ID
    tenant_b = uuid4()

    class_id = uuid4()
    subject_id = uuid4()

    academic_class = AcademicClass(
        id=class_id,
        tenant_id=tenant_a,
        name="6e Scientifique",
    )

    subject = Subject(
        id=subject_id,
        tenant_id=tenant_a,
        name="MathÃ©matiques",
        code="MATH",
        coefficient=3,
    )

    existing_other_tenant = ClassSubject(
        id=uuid4(),
        tenant_id=tenant_b,
        academic_class_id=class_id,
        subject_id=subject_id,
        coefficient=3,
    )

    class_repository = FakeAcademicClassRepository()
    subject_repository = FakeSubjectRepository()
    class_subject_repository = FakeClassSubjectRepository()
    class_option_repository = FakeClassOptionRepository()

    class_repository.add(academic_class)
    subject_repository.add(subject)
    class_subject_repository.save(existing_other_tenant)

    use_case = build_use_case(
        class_repository,
        subject_repository,
        class_subject_repository,
        class_option_repository,
    )

    result = use_case.execute(
        AssignSubjectToClassRequest(
            tenant_id=tenant_a,
            academic_class_id=class_id,
            subject_id=subject_id,
            coefficient=3,
        )
    )
    saved = class_subject_repository.find_by_class_and_option(
        class_id,
        None,
        tenant_a,
    )
    assert len(saved) == 1
    assert saved[0].tenant_id == tenant_a
    assert result.academic_class_id == class_id
    assert result.subject_id == subject_id

    saved = class_subject_repository.find_by_class_and_option(
        class_id,
        None,
        tenant_a,
    )

    assert len(saved) == 1
    assert saved[0].id == result.id
    assert saved[0].academic_class_id == result.academic_class_id
    assert saved[0].subject_id == result.subject_id
    assert saved[0].coefficient == result.coefficient
    assert saved[0].academic_option_id == result.academic_option_id
    assert saved[0].active == result.active










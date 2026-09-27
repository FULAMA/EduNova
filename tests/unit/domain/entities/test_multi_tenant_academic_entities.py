from uuid import uuid4





from src.academic.domain.entities.academic_class import AcademicClass

from src.academic.domain.entities.class_option import ClassOption


from src.academic.domain.entities.academic_option import AcademicOption


from src.academic.domain.entities.class_subject import ClassSubject


from src.academic.domain.entities.subject import Subject







def test_academic_class_belongs_to_tenant():


    tenant_id = uuid4()





    academic_class = AcademicClass(


        id=uuid4(),


        tenant_id=tenant_id,


        name="6e Informatique",


    )





    assert academic_class.tenant_id == tenant_id








def test_subject_belongs_to_tenant():


    tenant_id = uuid4()





    subject = Subject(


        id=uuid4(),


        tenant_id=tenant_id,


        name="MathÃƒÂ©matiques",


        code="MATH",


        coefficient=3,


    )





    assert subject.tenant_id == tenant_id








def test_academic_option_belongs_to_tenant():


    tenant_id = uuid4()





    option = AcademicOption(


        id=uuid4(),


        tenant_id=tenant_id,


        name="Informatique",


        code="INFO",


    )





    assert option.tenant_id == tenant_id








def test_class_option_belongs_to_tenant():


    tenant_id = uuid4()





    class_option = ClassOption(


        id=uuid4(),


        tenant_id=tenant_id,


        academic_class_id=uuid4(),


        academic_option_id=uuid4(),


    )





    assert class_option.tenant_id == tenant_id








def test_class_subject_belongs_to_tenant():


    tenant_id = uuid4()





    class_subject = ClassSubject(


        id=uuid4(),


        tenant_id=tenant_id,


        academic_class_id=uuid4(),


        subject_id=uuid4(),


        coefficient=3,


    )





    assert class_subject.tenant_id == tenant_id





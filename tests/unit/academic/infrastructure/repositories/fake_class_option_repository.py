class FakeClassOptionRepository:
    def __init__(self):
        self.items = {}

    def save(self, class_option):
        self.items[class_option.id] = class_option

    def find_by_id(self, class_option_id):
        return self.items.get(class_option_id)

    def find_by_class_and_option(
        self,
        academic_class_id,
        academic_option_id,
    ):
        for item in self.items.values():
            if (
                item.academic_class_id == academic_class_id
                and item.academic_option_id == academic_option_id
            ):
                return item

        return None

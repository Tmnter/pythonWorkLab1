class DomainError(Exception):
    """Базовий виняток предметної області."""
    pass


class EntityNotFound(DomainError):
    """Викликається, коли елемент не знайдено в колекції."""
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        super().__init__(f"Сутність з ідентифікатором '{entity_id}' не знайдено.")
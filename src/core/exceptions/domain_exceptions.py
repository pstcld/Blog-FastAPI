class DomainError(Exception):
    def __init__(self, message: str, details: dict = None):
        """Инициализация ошибки с сообщением и контекстными деталями."""
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityAlreadyExistsError(DomainError):
    pass


class EntityNotFoundError(DomainError):
    pass

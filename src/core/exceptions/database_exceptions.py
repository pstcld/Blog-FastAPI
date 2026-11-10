class DatabaseError(Exception):
    pass


class RecordAlreadyExistsError(DatabaseError):
    pass


class RecordNotFoundError(DatabaseError):
    pass

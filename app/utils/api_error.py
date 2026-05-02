from http import HTTPStatus


class ApiError(Exception):
    def __init__(self, status_code: int, message: str, is_operational: bool = True):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.is_operational = is_operational

    @classmethod
    def bad_request(cls, message: str = "Bad Request"):
        return cls(HTTPStatus.BAD_REQUEST, message)

    @classmethod
    def unauthorized(cls, message: str = "Please authenticate"):
        return cls(HTTPStatus.UNAUTHORIZED, message)

    @classmethod
    def forbidden(cls, message: str = "Forbidden"):
        return cls(HTTPStatus.FORBIDDEN, message)

    @classmethod
    def not_found(cls, message: str = "Not found"):
        return cls(HTTPStatus.NOT_FOUND, message)

    @classmethod
    def conflict(cls, message: str = "Conflict"):
        return cls(HTTPStatus.CONFLICT, message)

    @classmethod
    def internal(cls, message: str = "Internal Server Error"):
        return cls(HTTPStatus.INTERNAL_SERVER_ERROR, message, is_operational=False)

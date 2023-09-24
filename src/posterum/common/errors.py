from typing import Any


class PosterumError(Exception):
    code: int = 500
    message: str = "Internal Server Error"
    payload: dict[str, Any] = {}

    def __init__(self, message: str = "Internal Server Error", code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code


class UserError(PosterumError):
    def __init__(self, message: str = "User Error", code: int = 400):
        super().__init__(message, code)


class NotFoundError(UserError):
    def __init__(self, message: str = "Not Found Error", code: int = 404):
        super().__init__(message, code)

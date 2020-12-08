class PasswordTooShortError(BaseException):
    pass


class InvalidCredentialsError(BaseException):
    pass


class EmailMatchesPasswordError(BaseException):
    pass


class OutdatedPasswordVersionError(BaseException):
    pass
class DomainException(Exception):
    """Exceção base do domínio."""

    def __init__(self, message: str, code: str = "domain_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class EntityNotFoundError(DomainException):
    def __init__(self, entity: str, identifier: str) -> None:
        super().__init__(f"{entity} não encontrado: {identifier}", "not_found")


class AuthenticationError(DomainException):
    def __init__(self, message: str = "Credenciais inválidas") -> None:
        super().__init__(message, "authentication_error")


class AuthorizationError(DomainException):
    def __init__(self, message: str = "Acesso não autorizado") -> None:
        super().__init__(message, "authorization_error")


class AccountPendingApprovalError(AuthorizationError):
    def __init__(self, email: str) -> None:
        super().__init__(
            "Conta criada com sucesso. Aguarde aprovação de um administrador antes de entrar."
        )
        self.code = "account_pending_approval"
        self.email = email


class ValidationError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message, "validation_error")


class ConflictError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message, "conflict_error")

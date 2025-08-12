from typing import (Any,
                    Optional)


class DomruIntercomAPIError(Exception):
    """"""


class AuthDataRequiredDomruIntercomAPIError(DomruIntercomAPIError):
    def __init__(self, message: Optional[Any] = None):
        message = message or 'mess'
        super().__init__(message)


class ClientConnectorDomruIntercomAPIError(DomruIntercomAPIError):
    """"""


class UnauthorizedDomruIntercomAPIError(DomruIntercomAPIError):
    """"""


class TimeoutDomruIntercomAPIError(DomruIntercomAPIError):
    """"""


class UnknownDomruIntercomAPIError(DomruIntercomAPIError):
    """"""

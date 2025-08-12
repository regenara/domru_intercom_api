from typing import (Any,
                    Optional)


class DomruIntercomAPIError(Exception):
    """"""


class AuthDataRequiredDomruIntercomAPIError(DomruIntercomAPIError):
    def __init__(self, message: Optional[Any] = None):
        message = message or ('\n------------------------------------------------------------\n'
                              'domru_api = DomruIntercomAPI(login=LOGIN, password=PASSWORD)\n'
                              'OR\n'
                              'domru_api = DomruIntercomAPI(access_token=ACCESS_TOKEN)'
                              '\n------------------------------------------------------------\n')
        super().__init__(message)


class ClientConnectorDomruIntercomAPIError(DomruIntercomAPIError):
    """"""


class UnauthorizedDomruIntercomAPIError(DomruIntercomAPIError):
    """"""


class TimeoutDomruIntercomAPIError(DomruIntercomAPIError):
    """"""


class UnknownDomruIntercomAPIError(DomruIntercomAPIError):
    """"""

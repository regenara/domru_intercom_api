import asyncio
import base64
import certifi
import hashlib
import logging
import ssl
from datetime import (datetime,
                      timezone)
from json.decoder import JSONDecodeError
from typing import (Any,
                    Dict,
                    List,
                    Literal,
                    Optional,
                    Union)
from urllib.parse import (urljoin,
                          urlparse)
from uuid import uuid4

from aiohttp import (ClientSession,
                     ClientTimeout,
                     TCPConnector)
from aiohttp.client_exceptions import (ClientConnectorError,
                                       ContentTypeError)

from .exceptions import (AuthDataRequiredDomruIntercomAPIError,
                         ClientConnectorDomruIntercomAPIError,
                         DeviceUnavailableDomruIntercomAPIError,
                         TemporaryCodeFailedDomruIntercomAPIError,
                         TimeoutDomruIntercomAPIError,
                         UnauthorizedDomruIntercomAPIError,
                         UnknownDomruIntercomAPIError)
from .logger import SafeLogger
from .schemas import (DeviceSchema,
                      ErrorSchema,
                      EventSchema,
                      OpenResultSchema,
                      RefreshSchema,
                      SubscriberPlaceSchema,
                      TemporalCodeSchema,
                      TokenSchema)


class DomruIntercomAPI:
    def __init__(self, login: Optional[str] = None, password: Optional[str] = None,
                 refresh_token: Optional[str] = None, operator_id: Optional[int] = None,
                 timeout: int = 5, level: logging = logging.INFO):
        self._login: Optional[str] = login
        self._password: Optional[str] = password
        self._refresh_token: Optional[str] = refresh_token
        self._operator_id: Optional[int] = operator_id
        self._access_token: Optional[str] = None
        self._hash2_prefix: str = 'DigitalHomeNTKpassword'
        self._secret: str = '789sdgHJs678wertv34712376'
        self._base_url: str = 'https://myhome.proptech.ru/'
        self._headers: Dict[str, str] = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Host': urlparse(self._base_url).netloc,
            'User-Agent': 'Xiaomi MIX2S | Android 10 | erth | 8.26.0 (82600010) | | null | '
                          'd5c78d0a-9cbe-4bea-b66a-b8296d947b62 | null'
        }
        self._logger = SafeLogger('DomruIntercomAPI')
        self._logger.setLevel(level)

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.session: ClientSession = ClientSession(connector=TCPConnector(ssl=ssl_context),
                                                    timeout=ClientTimeout(total=timeout))

    async def _send_request(self, url: str, method: str = 'GET', params: Dict[str, Any] = None,
                            json: Dict[str, Any] = None,
                            headers: Dict[str, Any] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        while True:
            headers_ = headers or {
                'Authorization': f'Bearer {self._access_token}',
                **self._headers
            }
            request_id = uuid4().hex
            self._logger.info('Request=%s method=%s url=%s params=%s json=%s headers=%s',
                              request_id, method, url, params, json, headers_)
            try:
                async with self.session.request(method, url, params=params, json=json, headers=headers_) as response:
                    if response.status == 401:
                        raise UnauthorizedDomruIntercomAPIError(await response.text())
                    json_response = await response.json()

                    error_response = ErrorSchema()
                    if isinstance(json_response, str):
                        error_response.error_message = json_response
                    if isinstance(json_response, dict):
                        error_response = ErrorSchema(**json_response)

                    if response.status == 403:
                        self._logger.error('Response=%s AuthDataRequiredDomruIntercomAPIError json_response=%s',
                                           request_id, json_response)
                        raise AuthDataRequiredDomruIntercomAPIError(error_response.error_message or json_response)

                    if response.status == 531 and error_response.error_code == 6007:
                        self._logger.error('Response=%s DeviceUnavailableDomruIntercomAPIError json_response=%s',
                                           request_id, json_response)
                        raise DeviceUnavailableDomruIntercomAPIError(error_response.error_message)

                    if response.status == 500 and error_response.error_code == 6005:
                        self._logger.error('Response=%s TemporaryCodeFailedDomruIntercomAPIError json_response=%s',
                                           request_id, json_response)
                        raise TemporaryCodeFailedDomruIntercomAPIError(error_response.error_message)

                    if response.status not in (200,):
                        self._logger.error('Response=%s unsuccessful request json_response=%s status=%s reason=%s',
                                           request_id, json_response, response.status, response.reason)
                        raise UnknownDomruIntercomAPIError(error_response.error_message or json_response)

                    self._logger.info('Response=%s json_response=%s', request_id, json_response)
                    return json_response

            except (JSONDecodeError, ContentTypeError) as e:
                raw_response = await response.text()
                self._logger.error('Response=%s unsuccessful request status=%s reason=%s raw=% error=%s',
                                   request_id, response.status, response.reason, raw_response, e)
                raise UnknownDomruIntercomAPIError(f'Unknown error: {response.status} {response.reason}')

            except asyncio.exceptions.TimeoutError:
                self._logger.error('Response=%s TimeoutDomruIntercomAPIError', request_id)
                raise TimeoutDomruIntercomAPIError('Timeout error')

            except ClientConnectorError:
                self._logger.error('Response=%s ClientConnectorDomruIntercomAPIError', request_id)
                raise ClientConnectorDomruIntercomAPIError('Client connector error')

            except UnauthorizedDomruIntercomAPIError as e:
                self._logger.error('Response=%s UnauthorizedDomruIntercomAPIError=%s, trying get access_token',
                                   request_id, e)
                await self._set_access_token()

    @property
    def refresh_data(self) -> RefreshSchema:
        return RefreshSchema(refresh_token=self._refresh_token, operator_id=self._operator_id)

    def _get_hash1(self) -> str:
        password_bytes = self._password.encode('iso-8859-1')
        sha1_digest = hashlib.sha1(password_bytes).digest()
        hash1 = base64.b64encode(sha1_digest).decode('utf-8')
        return hash1

    def _get_hash2(self, timestamp: datetime) -> str:
        string = f'{self._hash2_prefix}{self._login}{self._password}{timestamp.strftime("%Y%m%d%H%M%S")}{self._secret}'
        hash2 = hashlib.md5(string.encode('utf-8')).hexdigest()
        return hash2

    async def _set_access_token(self):
        def _set_tokens(token_data: dict[str, Any]):
            _token = TokenSchema(**token_data)
            self._access_token = _token.access_token
            self._refresh_token = _token.refresh_token
            self._operator_id = _token.operator_id

        if self._refresh_token is not None and self._operator_id is not None:
            headers = {
                'Bearer': self._refresh_token,
                'Operator': str(self._operator_id)
            }
            url = urljoin(self._base_url, '/auth/v2/session/refresh')
            result = await self._send_request(url=url, headers=headers)
            _set_tokens(token_data=result)

        elif self._login is not None and self._password is not None:
            url = urljoin(self._base_url, f'auth/v2/auth/{self._login}/password')
            timestamp = datetime.now(timezone.utc)
            json = {
                'login': str(self._login),
                'timestamp': timestamp.isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
                'hash1': self._get_hash1(),
                'hash2': self._get_hash2(timestamp=timestamp)
            }
            result = await self._send_request(url=url, method='POST', json=json, headers=self._headers)
            _set_tokens(token_data=result)

        else:
            raise AuthDataRequiredDomruIntercomAPIError

    async def get_subscriber_places(self) -> List[SubscriberPlaceSchema]:
        url = urljoin(self._base_url, 'rest/v3/subscriber-places')
        result = await self._send_request(url=url)
        return [SubscriberPlaceSchema(**p) for p in result['data']]

    async def get_devices(self, place_id: int) -> List[DeviceSchema]:
        url = urljoin(self._base_url, f'rest/v1/places/{place_id}/accesscontrols')
        result = await self._send_request(url=url)
        return [DeviceSchema(**d) for d in result['data']]

    async def open_intercom(self, place_id: int, device_id: int) -> OpenResultSchema:
        url = urljoin(self._base_url, f'rest/v1/places/{place_id}/accesscontrols/{device_id}/actions')
        json = {
            'name': 'accessControlOpen'
        }
        result = await self._send_request(url=url, method='POST', json=json)
        return OpenResultSchema(**result['data'])

    async def get_events(self, *place_ids: int, page: int = 0,
                         sort: Literal['ASC', 'DESC'] = 'DESC') -> List[EventSchema]:
        url = urljoin(self._base_url, 'rest/v1/events/search')
        params = {
            'page': page,
            'sort': f'occurredAt,{sort}'
        }
        json = {
            'placeIds': place_ids
        }
        result = await self._send_request(url=url, method='POST', params=params, json=json)
        return [EventSchema(**e) for e in result['content']]

    async def get_temporal_codes(self, *device_ids: int) -> list[TemporalCodeSchema]:
        url = urljoin(self._base_url, 'rest/v1/temporal-codes')
        params = {
            'accessControlIds': ','.join(map(str, device_ids))
        }
        result = await self._send_request(url=url, params=params)
        return [TemporalCodeSchema(**d) for d in result]

    async def close(self):
        await self.session.close()

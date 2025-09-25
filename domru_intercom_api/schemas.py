from datetime import datetime
from typing import (Any,
                    List,
                    Optional)

from pydantic import (BaseModel as PydanticBaseModel,
                      ConfigDict)


def to_camel(s: str) -> str:
    parts = s.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TokenSchema(BaseModel):
    operator_id: int
    operator_name: str
    token_type: Optional[str]
    access_token: str
    expires_in: Optional[Any]
    refresh_token: str
    refresh_expires_in: Optional[Any]


class AddressSchema(BaseModel):
    index: Optional[Any]
    region: str
    district: Optional[Any]
    city: str
    locality: Optional[Any]
    street: str
    house: str
    building: Optional[Any]
    apartment: Optional[Any]
    visible_address: str
    group_name: str


class LocationSchema(BaseModel):
    longitude: float
    latitude: float


class PlaceSchema(BaseModel):
    id: int
    address: AddressSchema
    location: LocationSchema
    operator_id: int
    auto_arming_state: bool
    auto_arming_radius: int


class SubscriberSchema(BaseModel):
    id: int
    name: str
    account_id: str
    nick_name: Optional[Any]


class GuardCallOutSchema(BaseModel):
    active: bool
    phone_number: str


class PaymentSchema(BaseModel):
    use_link: bool


class SubscriberPlaceSchema(BaseModel):
    id: int
    subscriber_type: str
    subscriber_state: str
    place: PlaceSchema
    subscriber: SubscriberSchema
    guard_call_out: GuardCallOutSchema
    payment: PaymentSchema
    provider: str
    blocked: bool


class DeviceSchema(BaseModel):
    id: int
    operator_id: int
    name: str
    forpost_group_id: str
    forpost_account_id: Optional[Any]
    type: str
    allow_open: bool
    open_method: str
    allow_video: bool
    allow_call_mobile: bool
    allow_slideshow: bool
    preview_available: bool
    video_download_available: bool
    time_zone: int
    quota: int
    external_camera_id: str
    external_device_id: Optional[Any]


class OpenResultSchema(BaseModel):
    status: bool
    errorCode: Optional[int]
    errorMessage: Optional[str]


class SourceSchema(BaseModel):
    type: str
    id: int


class ValueSchema(BaseModel):
    type: str
    value: bool


class EventSchema(BaseModel):
    id: str
    place_id: int
    event_type_name: str
    timestamp: str
    message: str
    source: SourceSchema
    value: ValueSchema
    event_status_value: Optional[Any]
    actions: List


class RefreshSchema(BaseModel):
    refresh_token: Optional[str]
    operator_id: Optional[int]


class TemporalCodeSchema(BaseModel):
    code: str
    update_date: datetime
    access_control_id: int
    type: str


class ErrorSchema(BaseModel):
    error: Optional[str] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None

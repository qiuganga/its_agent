from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


def _non_empty(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("must not be empty")
    return value


class TextData(BaseModel):
    text: str = ""


class SearchWebInput(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        return _non_empty(value)


class SearchWebItem(BaseModel):
    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    source: str | None = None


class SearchWebData(BaseModel):
    items: list[SearchWebItem] = Field(default_factory=list)
    text: str | None = None


class GeocodeDestinationInput(BaseModel):
    address: str

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        return _non_empty(value)


class GeocodeDestinationData(BaseModel):
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    formatted_address: str | None = None


class ResolveUserLocationInput(BaseModel):
    user_input: str = ""


class LocationData(BaseModel):
    lat: float | None = None
    lng: float | None = None
    source: str
    address: str | None = None
    fallback: bool = False


class MapNavigationInput(BaseModel):
    origin: str
    destination: str
    mode: str = "driving"
    region: str = "北京"

    @field_validator("origin", "destination", "mode", "region")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return _non_empty(value)


class MapNavigationData(BaseModel):
    url: str | None = None
    markdown_link: str | None = None
    origin: str | None = None
    destination: str | None = None
    mode: str | None = None


class QueryNearestRepairShopsInput(BaseModel):
    lat: float
    lng: float
    limit: int = Field(default=3, ge=1, le=20)


class RepairShopItem(BaseModel):
    id: int | None = None
    service_station_name: str | None = None
    address: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_km: float | None = None


class QueryNearestRepairShopsData(BaseModel):
    items: list[RepairShopItem] = Field(default_factory=list)
    count: int = 0
    lat: float
    lng: float
    limit: int

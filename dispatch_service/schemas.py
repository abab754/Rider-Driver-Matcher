from pydantic import BaseModel, ConfigDict
from typing import Optional

class DriverInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    latitude: float
    longitude: float

class RiderInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    latitude: float
    longitude: float

class CreateDriver(BaseModel):
    name: str
    latitude: float
    longitude: float

class CreateRider(BaseModel):
    name: str
    latitude: float
    longitude: float

class TripRequest(BaseModel):
    rider_id: int
    dropoff_lat: float
    dropoff_long: float

class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    driver_id: Optional[int]=None
    price: Optional[float]=None
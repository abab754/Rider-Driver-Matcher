from sqlalchemy import String, Numeric, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from dispatch_service.database import Base

class Driver(Base):
    __tablename__ = "drivers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # Latitude ranges from -90 to 90 degrees (needs 8 total digits, 6 after decimal)
    latitude: Mapped[float] = mapped_column(Numeric(precision=8, scale=6), nullable=False)
    
    # Longitude ranges from -180 to 180 degrees (needs 9 total digits, 6 after decimal)
    longitude: Mapped[float] = mapped_column(Numeric(precision=9, scale=6), nullable=False)

    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

class Rider(Base):
    __tablename__ = "riders"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # Latitude ranges from -90 to 90 degrees (needs 8 total digits, 6 after decimal)
    latitude: Mapped[float] = mapped_column(Numeric(precision=8, scale=6), nullable=False)
    
    # Longitude ranges from -180 to 180 degrees (needs 9 total digits, 6 after decimal)
    longitude: Mapped[float] = mapped_column(Numeric(precision=9, scale=6), nullable=False)

class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(primary_key=True)
    rider_id: Mapped[int] = mapped_column(ForeignKey("riders.id"))
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id"))
    status: Mapped[str] = mapped_column(String(25))
    price: Mapped[Optional[float]] = mapped_column(Float)
    pickup_lat: Mapped[float] = mapped_column(Numeric(precision=8, scale=6), nullable=False)
    pickup_long: Mapped[float] = mapped_column(Numeric(precision=9, scale=6), nullable=False)
    dropoff_lat: Mapped[float] = mapped_column(Numeric(precision=8, scale=6), nullable=False)
    dropoff_long: Mapped[float] = mapped_column(Numeric(precision=9, scale=6), nullable=False)

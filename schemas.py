from pydantic import BaseModel, Field
from typing import Optional

class Tour(BaseModel):
    title: str = Field(..., description="Tour name")
    description: str = Field(..., description="What guests will experience")
    price: float = Field(..., ge=0)
    duration_hours: int = Field(..., ge=1)
    location: str = Field(..., description="Where the tour starts")
    image_url: Optional[str] = None
    featured: bool = False

class Vehicle(BaseModel):
    name: str
    type: str = Field(..., description="Car, SUV, Jeep, Scooter, Boat")
    seats: int = Field(..., ge=1)
    price_per_day: float = Field(..., ge=0)
    transmission: str = Field(..., description="Automatic/Manual")
    image_url: Optional[str] = None
    available: bool = True

class Booking(BaseModel):
    kind: str = Field(..., description="tour or vehicle")
    item_id: str
    name: str
    email: str
    phone: Optional[str] = None
    date: str
    notes: Optional[str] = None

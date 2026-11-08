from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ===========ROLE===========
class RoleOut(BaseModel):
    id: int
    role_name: str

    model_config = ConfigDict(from_attributes=True)


# ==========USER================
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    is_active: bool | None = None


class UserOut(UserBase):
    id: int
    role: RoleOut
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===========EVENT===========
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    location: str = Field(..., min_length=1, max_length=255)
    event_date: datetime
    total_seats: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0, decimal_places=2)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    location: str | None = Field(None, min_length=1, max_length=255)
    event_date: datetime | None = None
    total_seats: int | None = Field(None, gt=0)
    price: Decimal | None = Field(None, ge=0, decimal_places=2)


class EventOut(EventBase):
    id: int
    created_by: int
    available_seats: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===========BOOKING===========
class BookingCreate(BaseModel):
    event_id: int
    quantity: int = Field(..., gt=0)


class BookingStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(PENDING|CONFIRMED|CANCELLED)$")


class BookingOut(BaseModel):
    id: int
    user_id: int
    event_id: int
    quantity: int
    total_price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    # Optional nested details for rich API responses
    event: EventOut | None = None

    model_config = ConfigDict(from_attributes=True)


# ===========AUTH===========
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None

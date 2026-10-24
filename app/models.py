from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, Identity(), primary_key=True)
    role_name = Column(String(50), nullable=False, unique=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Identity(), primary_key=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, Identity(), primary_key=True)
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    event_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    __table_args__ = (
        CheckConstraint("available_seats >= 0", name="check_positive_available_seats"),
        CheckConstraint(
            "available_seats <= total_seats", name="check_valid_available_seats"
        ),
    )


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    event_id = Column(
        Integer,
        ForeignKey("events.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, server_default="PENDING")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_positive_quantity"),
        CheckConstraint(
            "status IN ('PENDING', 'CONFIRMED', 'CANCELLED')",
            name="check_valid_booking_status",
        ),
        CheckConstraint("total_price >= 0", name="check_positive_total_price"),
    )

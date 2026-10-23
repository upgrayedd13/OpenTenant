from enum import StrEnum
from sqlalchemy import Integer, String, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .model_base import ModelBase
from .mixins.id import IdMixin
from .mixins.timestamp import TimestampMixin


class ElevatorStatus(StrEnum):
    WORKING = "working"
    NON_WORKING = "non-working"
    RESERVED = "reserved"


class Elevator(IdMixin, TimestampMixin, ModelBase):
    __tablename__ = 'elevators'

    car_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    status: Mapped[ElevatorStatus] = mapped_column(
        String(20),
        default=ElevatorStatus.WORKING,
        nullable=False
    )
    comment: Mapped[str | None] = mapped_column(String(160), nullable=True)

    __table_args__ = (
        CheckConstraint('car_number >= 1 AND car_number <= 3', name='check_car_number_range'),
    )

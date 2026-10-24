from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .model_base import ModelBase
from .mixins.id import IdMixin
from .mixins.timestamp import TimestampMixin


class ElevatorStatusHistory(IdMixin, TimestampMixin, ModelBase):
    __tablename__ = 'elevator_status_history'

    elevator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('elevators.id', ondelete='CASCADE'), nullable=False
    )
    car_number: Mapped[int] = mapped_column(Integer, nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )
    comment: Mapped[str | None] = mapped_column(String(160), nullable=True)

    elevator = relationship("Elevator", back_populates="status_history")
    changed_by_user = relationship("User", back_populates="elevator_status_history")

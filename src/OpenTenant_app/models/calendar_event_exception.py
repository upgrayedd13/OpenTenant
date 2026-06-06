from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from typing import TYPE_CHECKING
from datetime import datetime

from .calendar_event_constants import TIME_FORMAT
from ..extensions import db
if TYPE_CHECKING:
    from .calendar_event import CalendarEvent


class CalendarEventException(db.Model):
    __tablename__ = 'calendar_event_exceptions'

    id:             Mapped[int]             = mapped_column(Integer, primary_key=True)
    event_id:       Mapped[int]             = mapped_column(ForeignKey('calendar_events.id'), nullable=False)
    exception_date: Mapped[datetime]        = mapped_column(DateTime(timezone=True), nullable=False)
    event:          Mapped['CalendarEvent'] = relationship(back_populates='exceptions')

    @staticmethod
    def from_dict(data: dict) -> 'CalendarEventException':
        if not isinstance(data, dict):
            raise ValueError('Invalid JSON')

        if 'exception_date' not in data:
            raise ValueError('Bad exception date')

        try:
            exception_date = datetime.strptime(data['exception_date'], TIME_FORMAT)
        except ValueError:
            raise ValueError('Bad exception date')

        return CalendarEventException(
            exception_date=exception_date,
        )
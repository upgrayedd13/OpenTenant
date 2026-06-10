from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from typing import TYPE_CHECKING
from datetime import datetime

from ..extensions import db
if TYPE_CHECKING:
    from .calendar_event import CalendarEvent


class CalendarEventException(db.Model):
    __tablename__ = 'calendar_event_exceptions'

    id:             Mapped[int]             = mapped_column(Integer, primary_key=True)
    event_id:       Mapped[int]             = mapped_column(ForeignKey('calendar_events.id'), nullable=False)
    exception_date: Mapped[datetime]        = mapped_column(DateTime(timezone=True), nullable=False)
    event:          Mapped['CalendarEvent'] = relationship(back_populates='exceptions')
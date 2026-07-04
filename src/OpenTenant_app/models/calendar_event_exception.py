from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import DateTime, ForeignKey
from typing import TYPE_CHECKING
from datetime import datetime

from .mixins import IdMixin, TimestampMixin, VersionedMixin
from .model_base import ModelBase
if TYPE_CHECKING:
    from .calendar_event import CalendarEvent


class CalendarEventException(ModelBase, IdMixin, TimestampMixin, VersionedMixin):
    __tablename__ = 'calendar_event_exceptions'

    event_id:       Mapped[int]             = mapped_column(ForeignKey('calendar_events.id'), nullable=False)
    exception_date: Mapped[datetime]        = mapped_column(DateTime(timezone=True), nullable=False)
    event:          Mapped['CalendarEvent'] = relationship(back_populates='exceptions')

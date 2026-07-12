from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from ..mixins import IdMixin, TimestampMixin, VersionedMixin
from ..model_base import ModelBase
if TYPE_CHECKING:
    from .calendar_event import CalendarEvent


class CalendarEventException(ModelBase, IdMixin, TimestampMixin, VersionedMixin):
    __tablename__ = 'calendar_event_exceptions'

    event_id:       Mapped[int]             = mapped_column(ForeignKey('calendar_events.id'), nullable=False)
    exception_date: Mapped[datetime]        = mapped_column(DateTime, nullable=False)
    event:          Mapped['CalendarEvent'] = relationship(back_populates='exceptions')

    @staticmethod
    def from_dict(data: dict) -> 'CalendarEventException':
        # sanity checks
        if not isinstance(data, dict):
            raise ValueError('Invalid JSON')
        elif 'exception_date' not in data:
            raise ValueError('Bad exception date')

        # get the date
        value = data['exception_date']
        if not isinstance(value, str):
            raise ValueError('Bad exception date')

        # parse ISO 8601 (frontend sends ISO)
        try:
            dt = datetime.fromisoformat(value)
        except Exception:
            raise ValueError('Bad exception date format (expected ISO 8601)')

        # parse the timezone
        try:
            tz = ZoneInfo(data['timezone'])
        except Exception:
            raise ValueError(f'Invalid timezone "{data["timezone"]}"')

        # replace the timezone info and normalize to UTC
        dt = dt.replace(tzinfo=tz).astimezone(timezone.utc)

        # create the object
        return CalendarEventException(
            exception_date=dt,
        )

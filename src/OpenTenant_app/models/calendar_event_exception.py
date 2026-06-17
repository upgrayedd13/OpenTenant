from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import Integer, ForeignKey
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from .utc_date_time import UTCDateTime
from ..extensions import db
if TYPE_CHECKING:
    from .calendar_event import CalendarEvent


class CalendarEventException(db.Model):
    __tablename__ = 'calendar_event_exceptions'

    id:             Mapped[int]             = mapped_column(Integer, primary_key=True)
    event_id:       Mapped[int]             = mapped_column(ForeignKey('calendar_events.id'), nullable=False)
    exception_date: Mapped[datetime]        = mapped_column(UTCDateTime, nullable=False)
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

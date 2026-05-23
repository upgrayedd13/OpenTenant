from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import Integer, String, DateTime
from datetime import datetime, timezone
from dateutil.rrule import rrulestr
from typing import TYPE_CHECKING

from ..extensions import db
if TYPE_CHECKING:
    from .calendar_event_exception import CalendarEventException


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'

    id:            Mapped[int]      = mapped_column(Integer,  primary_key=True)
    title:         Mapped[str]      = mapped_column(String,   nullable=False)
    start_time:    Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time:      Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location:      Mapped[str|None] = mapped_column(String,   nullable=True)
    description:   Mapped[str|None] = mapped_column(String,   nullable=True)

    # RFC 5545 RRULE string (nullable means the event is non-repeating)
    rrule:         Mapped[str|None] = mapped_column(String,   nullable=True)

    # exceptions to the RRULE
    exceptions:    Mapped[list['CalendarEventException']] = relationship(back_populates='event', cascade='all, delete-orphan')


    @staticmethod
    def validate_rrule(value: str) -> None:
        try:
            rrulestr(value)
        except Exception:
            raise ValueError(f'Invalid RRULE "{value}"')


    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            raise ValueError('Datetime objects must be timezone-aware!')
        return dt.astimezone(timezone.utc)


    def get_occurrences(self, start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
        # normalize to UTC
        start       = CalendarEvent.to_utc(start)
        end         = CalendarEvent.to_utc(end)
        event_start = CalendarEvent.to_utc(self.start_time)
        event_end   = CalendarEvent.to_utc(self.end_time)

        # if no rrule, just return if our event is within the range
        if self.rrule is None:
            if start <= event_start <= end:
                return [(event_start, event_end)]
            return []

        # generate the datetimes in our range that follow the rrule
        rule = rrulestr(self.rrule, dtstart=event_start)
        datetimes = rule.between(start, end, inc=True)

        # set of exception dates
        exception_dates = {ex.exception_date for ex in self.exceptions}

        # filter the exceptions out and return a list of (start_time, endtime) datetime objects
        duration = event_end - event_start
        return [(dt, dt + duration) for dt in datetimes if dt not in exception_dates]

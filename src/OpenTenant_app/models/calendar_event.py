from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import String, DateTime, select, or_, and_
from datetime import datetime, timezone
from dateutil.rrule import rrulestr
from typing import Any

from .mixins import IdMixin, TimestampMixin, VersionedMixin, QueryMixin
from .calendar_event_exception import CalendarEventException
from ..schemas.calendar_event import CalendarEventSchema
from .model_base import ModelBase
from ..extensions import db


class CalendarEvent(ModelBase, IdMixin, TimestampMixin, VersionedMixin, QueryMixin):
    __tablename__ = 'calendar_events'

    title:         Mapped[str]      = mapped_column(String,   nullable=False)
    location:      Mapped[str|None] = mapped_column(String,   nullable=True)
    description:   Mapped[str|None] = mapped_column(String,   nullable=True)

    # start and end datetime *of the first event*
    # if repeated, only the time portion of the object is used
    start_time:    Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time:      Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # RFC 5545 RRULE string (nullable means the event is non-repeating)
    rrule:         Mapped[str|None] = mapped_column(String,   nullable=True)

    # exceptions to the RRULE
    exceptions:    Mapped[list['CalendarEventException']] = relationship(back_populates='event', cascade='all, delete-orphan')


    @classmethod
    def from_dict(cls, data: dict) -> 'CalendarEvent':
        # Use the schema for validation and parsing
        validated_data = CalendarEventSchema.parse_and_validate(data)

        # Parse exceptions to the recurrences
        exceptions_raw = validated_data.pop('exceptions')
        tz_name = validated_data.pop('timezone')
        if not all(isinstance(e, dict) for e in exceptions_raw):
            raise ValueError('All date exceptions must be objects')

        # Pass the timezone to the exception parser
        exceptions = []
        for e in exceptions_raw:
            # Ensure the exception has the timezone from the main event if not provided
            if 'timezone' not in e:
                e = e.copy()
                e['timezone'] = tz_name
            exceptions.append(CalendarEventException.from_dict(e))

        # return the constructed object
        return cls(
            **validated_data,
            exceptions=exceptions,
        )


    @staticmethod
    def validate_rrule(value: str) -> None:
        CalendarEventSchema.validate_rrule(value)


    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)  # assume naive datetimes from the DB are already UTC
        return dt.astimezone(timezone.utc)


    @staticmethod
    def windows_overlap(w1: tuple[datetime, datetime], w2: tuple[datetime, datetime]) -> bool:
        # sanity checks
        if len(w1) != 2:
            raise ValueError(f'Expected 2 datetimes for w1 (got {len(w1)})!')
        if len(w2) != 2:
            raise ValueError(f'Expected 2 datetimes for w2 (got {len(w2)})!')
        elif w1[0] > w1[1]:
            raise ValueError(f'Window 1 is invalid ({w1[0]}, {w1[1]})!')
        elif w2[0] > w2[1]:
            raise ValueError(f'Window 2 is invalid ({w2[0]}, {w2[1]})!')

        # normalize to UTC
        w1_start = CalendarEvent.to_utc(w1[0])
        w1_end   = CalendarEvent.to_utc(w1[1])
        w2_start = CalendarEvent.to_utc(w2[0])
        w2_end   = CalendarEvent.to_utc(w2[1])

        # check for overlap
        return w1_start < w2_end and w1_end > w2_start


    @staticmethod
    def get_events(start: datetime, end: datetime) -> list[dict[str, Any]]:
        # normalize to UTC
        start = CalendarEvent.to_utc(start)
        end   = CalendarEvent.to_utc(end)

        # get all events in the DB that either:
        #  - don't have an rrule and are within the time window
        #  - do have an rrule and start before the end of the window
        events: list[CalendarEvent] = list(db.session.execute(
            select(CalendarEvent).filter(
                or_(
                    and_(CalendarEvent.rrule.is_(None), CalendarEvent.start_time < end, CalendarEvent.end_time > start),
                    and_(CalendarEvent.rrule.isnot(None), CalendarEvent.start_time < end)
                )
            )
        ).scalars().all())

        # list of dictionaries representing events that we'll return
        event_list: list[dict[str, Any]] = list()

        # function to make event dictionary
        def add_event_dict(event: CalendarEvent, start_time: datetime, end_time: datetime) -> None:
            event_list.append({
                'id': event.id,
                'title': event.title,
                'location': event.location,
                'description': event.description,
                'start_time': start_time,
                'end_time': end_time,
                'rrule': event.rrule,
            })

        # for each event left
        for event in events:
            # get all occurrences that fall in our timeframe
            occurrences = event.get_occurrences(start, end)

            # create a dictionary for each occurrence
            for start_time, end_time in occurrences:
                add_event_dict(event, start_time, end_time)

        # finally, return the list of dictionaries
        return event_list


    def get_occurrences(self, start: datetime, end: datetime) -> list[tuple[datetime, datetime]]:
        # normalize to UTC
        start       = CalendarEvent.to_utc(start)
        end         = CalendarEvent.to_utc(end)
        event_start = CalendarEvent.to_utc(self.start_time)
        event_end   = CalendarEvent.to_utc(self.end_time)
        duration    = event_end - event_start

        # if no rrule, just return if our event overlaps the window
        if self.rrule is None:
            if CalendarEvent.windows_overlap((event_start, event_end), (start, end)):
                return [(event_start, event_end)]
            return []

        # widen the lower bound by the event's duration so we also catch
        # occurrences that started before `start` but whose end overlaps
        # into the window
        rule = rrulestr(self.rrule, dtstart=event_start)
        datetimes = rule.between(start - duration, end, inc=True)

        # set of exception dates
        exception_dates = {CalendarEvent.to_utc(ex.exception_date) for ex in self.exceptions}

        # build (start, end) pairs, drop exceptions, then keep only the
        # occurrences that actually overlap the requested window
        occurrences = [(dt, dt + duration) for dt in datetimes if dt not in exception_dates]
        return [occ for occ in occurrences if CalendarEvent.windows_overlap(occ, (start, end))]


    def to_dict(self) -> dict:
        return CalendarEventSchema.serialize(self)

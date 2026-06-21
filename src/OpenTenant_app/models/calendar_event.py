from sqlalchemy import Integer, String, DateTime, select, or_, and_
from sqlalchemy.orm import mapped_column, relationship, Mapped
from datetime import datetime, timezone
from dateutil.rrule import rrulestr
from zoneinfo import ZoneInfo
from typing import Any

from .calendar_event_exception import CalendarEventException
from .model_base import ModelBase
from ..extensions import db


class CalendarEvent(ModelBase):
    __tablename__ = 'calendar_events'

    id:            Mapped[int]      = mapped_column(Integer,  primary_key=True)
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
        # helper function to get values out of JSON data
        def get_val(k: str, *, type_: type|tuple[type, ...]|None=None, nullable: bool=False) -> Any:
            if k not in data:
                if nullable:
                    return None
                else:
                    raise ValueError(f'Missing field {k}')

            v = data[k]
            if v is None:
                if nullable:
                    return None
                raise ValueError(f'Missing value for field {k}')

            if type_ is not None and not isinstance(v, type_):
                type_name = type_.__name__ if isinstance(type_, type) else " or ".join(t.__name__ for t in type_)
                raise ValueError(f'Field {k} must be {type_name}')

            return v

        # ensure we were given a dictionary
        if not isinstance(data, dict):
            raise ValueError('Expected an object')

        # parse all the values
        title          = get_val('title',       type_=str)
        tz_name        = get_val('timezone',    type_=str)
        start_time_str = get_val('start_time',  type_=str)
        end_time_str   = get_val('end_time',    type_=str)
        location       = get_val('location',    type_=str,  nullable=True)
        description    = get_val('description', type_=str,  nullable=True)
        rrule          = get_val('rrule',       type_=str,  nullable=True)
        exceptions     = get_val('exceptions',  type_=list, nullable=True) or []

        # convert the timezone name to a ZoneInfo object
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            raise ValueError(f'Invalid timezone "{tz_name}"')

        # parse the start time strings as ISO8601
        try:
            start_naive = datetime.fromisoformat(start_time_str)
            end_naive   = datetime.fromisoformat(end_time_str)
        except Exception:
            raise ValueError('Invalid datetime format (expected ISO 8601)')

        # update the naive times with timezone info
        start = start_naive.replace(tzinfo=tz)
        end   = end_naive.replace(tzinfo=tz)

        # normalize the start/end times to UTC
        start = start.astimezone(timezone.utc)
        end   = end.astimezone(timezone.utc)

        # ensure the end time is after the start time
        if end <= start:
            raise ValueError('end_time must be after start_time')

        # check that the rrule is valid
        if rrule is not None:
            CalendarEvent.validate_rrule(rrule)

        # parse exceptions to the recurrences
        if exceptions is None:
            exceptions = []
        elif not all(isinstance(e, dict) for e in exceptions):
            raise ValueError('All date exceptions must be objects')
        else:
            exceptions = [CalendarEventException.from_dict(exception) for exception in exceptions]

        # return the constructed object
        return cls(
            title=title,
            start_time=start,
            end_time=end,
            location=location,
            description=description,
            rrule=rrule,
            exceptions=exceptions,
        )


    @staticmethod
    def validate_rrule(value: str) -> None:
        try:
            rrulestr(value)
        except Exception:
            raise ValueError(f'Invalid RRULE "{value}"')


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
        return {
            'id':          self.id,
            'title':       self.title,
            'location':    self.location,
            'description': self.description,
            'start_time':  self.start_time.isoformat(),
            'end_time':    self.end_time.isoformat(),
            'rrule':       self.rrule,
            "exceptions":  [ex.exception_date.isoformat() for ex in self.exceptions] if self.exceptions else [],
        }

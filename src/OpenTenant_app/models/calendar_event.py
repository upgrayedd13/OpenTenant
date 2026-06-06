from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import Integer, String, DateTime, or_, and_
from datetime import datetime, timezone
from dateutil.rrule import rrulestr
from typing import Any

from .calendar_event_exception import CalendarEventException
from .calendar_event_constants import TIME_FORMAT
from ..extensions import db

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'

    id:            Mapped[int]      = mapped_column(Integer,  primary_key=True)
    title:         Mapped[str]      = mapped_column(String,   nullable=False)
    location:      Mapped[str|None] = mapped_column(String,   nullable=True)
    description:   Mapped[str|None] = mapped_column(String,   nullable=True)

    # start and end datetime *of the first event*
    # if repeated, only the time portion of the object is used
    start_time:    Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time:      Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # RFC 5545 RRULE string (nullable means the event is non-repeating)
    rrule:         Mapped[str|None] = mapped_column(String,   nullable=True)

    # exceptions to the RRULE
    exceptions:    Mapped[list['CalendarEventException']] = relationship(back_populates='event', cascade='all, delete-orphan')


    @staticmethod
    def from_dict(data: dict) -> 'CalendarEvent':
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

        # get the raw values
        title       = get_val('title',       type_=str)
        start_time  = get_val('start_time',  type_=str)
        end_time    = get_val('end_time',    type_=str)
        location    = get_val('location',    type_=str,  nullable=True)
        description = get_val('description', type_=str,  nullable=True)
        rrule       = get_val('rrule',       type_=str,  nullable=True)
        exceptions  = get_val('exceptions',  type_=list, nullable=True)

        # parse the start and stop times
        try:
            start_time = datetime.strptime(start_time, TIME_FORMAT)
        except ValueError:
            raise ValueError('Failed to parse start_time string')

        try:
            end_time = datetime.strptime(end_time, TIME_FORMAT)
        except ValueError:
            raise ValueError('Failed to parse end_time string')

        if end_time <= start_time:
            raise ValueError('end_time must be after start_time')

        # check that the rrule is valid
        if rrule is not None:
            CalendarEvent.validate_rrule(rrule)

        # parse exceptions
        if exceptions is None:
            exceptions = []
        elif not all(isinstance(e, dict) for e in exceptions):
            raise ValueError('All date exceptions must be objects')
        else:
            exceptions = [CalendarEventException.from_dict(exception) for exception in exceptions]

        # generate the event object
        return CalendarEvent(
            title=title,
            start_time=start_time,
            end_time=end_time,
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
            raise ValueError('Datetime objects must be timezone-aware!')
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
        for window in [w1, w2]:
            for i in range(len(window)):
                window[i] = CalendarEvent.to_utc(window[i])

        # check for overlap
        return w1[0] < w2[1] and w1[1] > w2[0]


    @staticmethod
    def get_events(start: datetime, end: datetime) -> list[dict[str, Any]]:
        # normalize to UTC
        start = CalendarEvent.to_utc(start)
        end   = CalendarEvent.to_utc(end)

        # get all events in the DB that either:
        #  - don't have a rrule and are within the time window
        #  - do have an rrule and start before the end of the window
        events: list[CalendarEvent] = CalendarEvent.query.filter(
            or_(
                and_(CalendarEvent.rrule.is_(None), CalendarEvent.start_time >= start, CalendarEvent.end_time < end),
                and_(CalendarEvent.rrule.isnot(None), CalendarEvent.start_time < end)
            )
        ).all()

        # list of dictionaries representing events that we'll return
        event_list: list[dict[str, Any]] = list()

        # function to make event dictionary
        def add_event_dict(event: CalendarEvent, start_time: datetime, end_time: datetime) -> None:
            event_list.append({
                'title': event.title,
                'location': event.location,
                'description': event.description,
                'start_time': start_time,
                'end_time': end_time
            })

        # for each event left
        for event in events:
            if CalendarEvent.windows_overlap((event.start_time, event.end_time), (start, end)):
                add_event_dict(event, event.start_time, event.end_time)

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

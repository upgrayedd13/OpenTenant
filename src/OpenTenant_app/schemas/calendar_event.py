from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING
from dateutil.rrule import rrulestr
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from ..models.calendar_event import CalendarEvent


class CalendarEventSchema:
    @staticmethod
    def validate_rrule(value: str) -> None:
        try:
            rrulestr(value)
        except Exception:
            raise ValueError(f'Invalid RRULE "{value}"')


    @classmethod
    def parse_and_validate(cls, data: dict) -> dict:
        # ensure we were given a dictionary
        if not isinstance(data, dict):
            raise ValueError('Expected an object')

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
            cls.validate_rrule(rrule)

        return {
            'title': title,
            'start_time': start,
            'end_time': end,
            'location': location,
            'description': description,
            'rrule': rrule,
            'exceptions': exceptions,
            'timezone': tz_name
        }


    @classmethod
    def serialize(cls, event: 'CalendarEvent') -> dict:
        """Convert a CalendarEvent model instance into a dictionary for API responses."""
        return {
            'id':          event.id,
            'title':       event.title,
            'location':    event.location,
            'description': event.description,
            'start_time':  event.start_time.isoformat(),
            'end_time':    event.end_time.isoformat(),
            'rrule':       event.rrule,
            "exceptions":  [ex.exception_date.isoformat() for ex in event.exceptions] if event.exceptions else [],
        }

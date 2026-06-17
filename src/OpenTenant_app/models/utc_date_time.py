from sqlalchemy.types import TypeDecorator, DateTime
from datetime import datetime, timezone

# NOTE: We need to do this because not all SQL dialects support DateTime objects
class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True
    
    def process_bind_param(self, value: datetime|None, dialect) -> datetime|None:
        if value is None:
            return None
        elif value.tzinfo is None:
            raise ValueError('Datetime objects must be timezone-aware!')
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime|None, dialect) -> datetime|None:
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc)
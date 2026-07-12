from sqlalchemy.orm import mapped_column, Mapped, validates
from sqlalchemy import String, Boolean

from .mixins import IdMixin, TimestampMixin, VersionedMixin
from .model_base import ModelBase


class ScheduledJob(ModelBase, IdMixin, TimestampMixin, VersionedMixin):
    __tablename__ = 'scheduled_jobs'

    name:      Mapped[str]      = mapped_column(String(128), unique=True, nullable=False)
    function:  Mapped[str]      = mapped_column(String(256), nullable=False)

    minute:    Mapped[int]      = mapped_column(String(10),  default='0')
    hour:      Mapped[int]      = mapped_column(String(10),  default='0')
    dom:       Mapped[str]      = mapped_column(String(10),  default='*')
    month:     Mapped[str]      = mapped_column(String(10),  default='*')
    dow:       Mapped[str]      = mapped_column(String(10),  default='*')

    enabled:   Mapped[bool]     = mapped_column(Boolean,     default=True)


    @validates('minute', 'hour', 'dom', 'month', 'dow')
    def validate_cron_field(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError(f'{key} must be a cron string')

        return value.strip()

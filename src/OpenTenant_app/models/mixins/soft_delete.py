from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import DateTime
from datetime import datetime


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

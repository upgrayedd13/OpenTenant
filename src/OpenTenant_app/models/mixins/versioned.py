from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer


class VersionedMixin:
    version_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    __mapper_args__ = {
        "version_id_col": version_id,
    }

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Uuid
import uuid


class PublicIdMixin:
    public_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        unique=True,
    )

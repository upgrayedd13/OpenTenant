from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer


class IdMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

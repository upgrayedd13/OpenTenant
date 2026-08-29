from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String
from typing import TYPE_CHECKING

from .mixins import IdMixin, TimestampMixin, VersionedMixin, QueryMixin
from .model_base import ModelBase

if TYPE_CHECKING:
    from .apartment_unit_snapshot import ApartmentUnitSnapshot


class ApartmentUnit(ModelBase, IdMixin, TimestampMixin, VersionedMixin, QueryMixin):
    __tablename__ = 'apartment_units'

    unit_id:    Mapped[str]  = mapped_column(String,  nullable=False, unique=True)
    unit_num:   Mapped[str]  = mapped_column(String,  nullable=True)
    sq_footage: Mapped[int]  = mapped_column(Integer, nullable=True)

    snapshots: Mapped[list['ApartmentUnitSnapshot']] = relationship(
        'ApartmentUnitSnapshot',
        back_populates='unit'
    )

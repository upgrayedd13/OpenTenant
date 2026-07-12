from sqlalchemy import Integer, Date, ForeignKey, Index, String
from sqlalchemy.orm import mapped_column, relationship, Mapped
from typing import TYPE_CHECKING
from datetime import date

from ..mixins import IdMixin, TimestampMixin, VersionedMixin
from ..model_base import ModelBase
if TYPE_CHECKING:
    from .apartment_inventory_snapshot import ApartmentInventorySnapshot


class ApartmentUnitSnapshot(ModelBase, IdMixin, TimestampMixin, VersionedMixin):
    __tablename__ = 'apartment_unit_snapshots'

    unit_id:        Mapped[str]  = mapped_column(String,  nullable=False)
    unit_num:       Mapped[str]  = mapped_column(String,  nullable=True)
    price:          Mapped[int]  = mapped_column(Integer, nullable=True)
    sq_footage:     Mapped[int]  = mapped_column(Integer, nullable=True)
    date_available: Mapped[date] = mapped_column(Date,    nullable=True)

    snapshot_id:    Mapped[int]  = mapped_column(Integer, ForeignKey('apartment_inventory_snapshots.id'), nullable=False)
    snapshot:       Mapped['ApartmentInventorySnapshot'] = relationship('ApartmentInventorySnapshot', back_populates='units')

    __table_args__ = (
        Index("index_unit_snapshot", "unit_id", "snapshot_id"),
        Index("index_snapshot", "snapshot_id"),
    )

from sqlalchemy import Integer, Date, ForeignKey, Index, String
from sqlalchemy.orm import mapped_column, relationship, Mapped
from typing import TYPE_CHECKING
from datetime import date

from .mixins import QueryMixin
from .model_base import ModelBase
if TYPE_CHECKING:
    from .apartment_inventory_snapshot import ApartmentInventorySnapshot
    from .apartment_unit import ApartmentUnit


class ApartmentUnitSnapshot(ModelBase, QueryMixin):
    __tablename__ = 'apartment_unit_snapshots'

    snapshot_id:    Mapped[int]  = mapped_column(ForeignKey('apartment_inventory_snapshots.id'), primary_key=True, nullable=False)
    unit_id:        Mapped[int]  = mapped_column(ForeignKey('apartment_units.id'), primary_key=True, nullable=False)

    price:          Mapped[int]  = mapped_column(Integer, nullable=True)
    date_available: Mapped[date] = mapped_column(Date,    nullable=True)

    unit: Mapped['ApartmentUnit'] = relationship(
        'ApartmentUnit',
        back_populates='snapshots',
    )

    snapshot: Mapped['ApartmentInventorySnapshot'] = relationship(
        'ApartmentInventorySnapshot',
        back_populates='units',
    )

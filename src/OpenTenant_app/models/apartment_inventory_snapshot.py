from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import JSON, DateTime
from typing import TYPE_CHECKING
from datetime import datetime

from .mixins import IdMixin, QueryMixin
from .model_base import ModelBase
if TYPE_CHECKING:
    from .apartment_unit_snapshot import ApartmentUnitSnapshot


class ApartmentInventorySnapshot(ModelBase, IdMixin, QueryMixin):
    __tablename__ = 'apartment_inventory_snapshots'

    snapshot_time:  Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_data:       Mapped[dict]     = mapped_column(JSON, nullable=False)

    units: Mapped[list['ApartmentUnitSnapshot']] = relationship(
        'ApartmentUnitSnapshot',
        back_populates='snapshot',
        cascade='all, delete-orphan',
    )

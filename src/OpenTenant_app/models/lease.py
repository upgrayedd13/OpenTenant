from sqlalchemy import Integer, Numeric, String, Date, CheckConstraint, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import date
import os

from ..utils import custom_validators as unum
from .model_base import ModelBase
if TYPE_CHECKING:
    from .user import User


MAX_LEASE_PATH_LEN = os.pathconf(os.getenv('LEASES_DIR', '/tmp/leases'), 'PC_PATH_MAX')


class Lease(ModelBase):
    __tablename__ = 'leases'

    id:                 Mapped[int]       = mapped_column(Integer,        primary_key=True)
    base_monthly_rent:  Mapped[Decimal]   = mapped_column(Numeric(10, 2), nullable=False)
    monthly_rent_total: Mapped[Decimal]   = mapped_column(Numeric(10, 2), nullable=False)
    unit_number:        Mapped[int]       = mapped_column(Integer,        nullable=False)
    num_occupants:      Mapped[int]       = mapped_column(Integer,        nullable=False)
    start_date:         Mapped[date]      = mapped_column(Date,           nullable=False)
    end_date:           Mapped[date|None] = mapped_column(Date,           nullable=True)   # might not have an end date?
    path:               Mapped[str]       = mapped_column(String(MAX_LEASE_PATH_LEN), nullable=False)

    user_id:            Mapped[int]       = mapped_column(ForeignKey('users.id'), nullable=False)
    user:               Mapped['User']    = relationship(back_populates='leases')

    __table_args__ = (
        CheckConstraint(
            f'''
            (((unit_number / 100) BETWEEN {unum.MIN_FLOOR} AND {unum.MAX_FLOOR-1}) AND ((unit_number % 100) BETWEEN {unum.MIN_UNIT} AND {unum.MAX_UNIT})) OR
            (((unit_number / 100) = {unum.MAX_FLOOR})                              AND ((unit_number % 100) BETWEEN {unum.MIN_UNIT} AND {unum.MAX_UNIT_TOP_FLOOR}))
            ''',
            name='valid_unit_number'
        ),
    )


    @property
    def floor(self) -> int:
        return self.unit_number // 100


    @property
    def unit(self) -> int:
        return self.unit_number % 100


    @staticmethod
    def str_field_len(field: str) -> int:
        column = Lease.__table__.c[field]
        length = getattr(column.type, 'length', None)
        if length is not None:
            return length
        return 256

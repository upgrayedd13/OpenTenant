from sqlalchemy import Integer, Float, String, Date, CheckConstraint, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from typing import TYPE_CHECKING
from datetime import date
import os

from ..utils import custom_validators as unum
from ..extensions import db
if TYPE_CHECKING:
    from .user import User


MAX_LEASE_PATH_LEN = os.pathconf(os.getenv('LEASES_DIR', '/tmp/leases'), 'PC_PATH_MAX')


class Lease(db.Model):
    __tablename__ = 'leases'

    id:                 Mapped[int]    = mapped_column(Integer,     primary_key=True)
    base_monthly_rent:  Mapped[float]  = mapped_column(Float,       nullable=False)
    monthly_rent_total: Mapped[float]  = mapped_column(Float,       nullable=False)
    unit_number:        Mapped[int]    = mapped_column(Integer,     nullable=False)
    start_date:         Mapped[date]   = mapped_column(Date,        nullable=False)
    end_date:           Mapped[date]   = mapped_column(Date,        nullable=True)   # might not have an end date?
    address:            Mapped[str]    = mapped_column(String(256), nullable=False)
    path:               Mapped[str]    = mapped_column(String(MAX_LEASE_PATH_LEN), nullable=False)

    user_id:            Mapped[int]    = mapped_column(ForeignKey('users.id'), nullable=False)
    user:               Mapped['User'] = relationship(back_populates='leases')

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
    def unumit(self) -> int:
        return self.unit_number % 100


    @staticmethod
    def str_field_len(field: str) -> int:
        return Lease.__table__.c[field].type.length

from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import Integer, String, ForeignKey
from typing import TYPE_CHECKING

from ..extensions import db
if TYPE_CHECKING:
    from .user import User


class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'

    id:            Mapped[int] = mapped_column(Integer,     primary_key=True)
    name:          Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number:  Mapped[str] = mapped_column(String(20),  nullable=False)

    user_id:       Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user:          Mapped['User'] = relationship(back_populates='emergency_contact')

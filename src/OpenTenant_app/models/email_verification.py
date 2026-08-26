from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, relationship, Mapped
from datetime import datetime
from typing import TYPE_CHECKING

from .mixins import IdMixin, TimestampMixin, QueryMixin
from .model_base import ModelBase
if TYPE_CHECKING:
    from .user import User


class EmailVerification(ModelBase, IdMixin, TimestampMixin, QueryMixin):
    __tablename__ = 'email_verifications'

    token_hash: Mapped[str]      = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_id:    Mapped[int]      = mapped_column(ForeignKey('users.id'), nullable=False, unique=True)
    user:       Mapped['User']   = relationship(back_populates='email_verification')

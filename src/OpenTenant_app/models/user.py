from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Integer, String
from flask_login import UserMixin
from typing import TYPE_CHECKING
from datetime import date
import logging

from .mixins import IdMixin, TimestampMixin, VersionedMixin
from ..extensions import login_manager, db
from .model_base import ModelBase
from .user_role import UserRole
if TYPE_CHECKING:
    from .lease import Lease


logger = logging.getLogger(__name__)


class User(ModelBase, UserMixin, IdMixin, TimestampMixin, VersionedMixin):
    __tablename__ = 'users'

    role:              Mapped[int]           = mapped_column(Integer,     nullable=False, default=UserRole.USER)
    username:          Mapped[str]           = mapped_column(String(50),  unique=True, nullable=False)
    email:             Mapped[str]           = mapped_column(String(254), unique=True, nullable=False)
    password_hash:     Mapped[str]           = mapped_column(String(256), nullable=False)
    name:              Mapped[str]           = mapped_column(String(150), nullable=False)
    phone_number:      Mapped[str|None]      = mapped_column(String(20),  nullable=True)
    pronouns:          Mapped[str|None]      = mapped_column(String(20),  nullable=True)
    leases:            Mapped[list['Lease']] = relationship(back_populates='user', order_by='Lease.start_date')

    @hybrid_property
    def current_lease(self) -> 'Lease | None':
        today = date.today()
        for lease in self.leases:
            if lease.start_date <= today and (lease.end_date is None or lease.end_date >= today):
                return lease
        return None


    @staticmethod
    def str_field_len(field: str) -> int:
        return User.__table__.c[field].type.length


    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


    def is_admin(self) -> bool:
        return self.role >= UserRole.ADMIN


@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    return db.session.get(User, int(user_id))

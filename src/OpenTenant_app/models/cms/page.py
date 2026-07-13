from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, Boolean

from ..mixins import IdMixin, TimestampMixin, VersionedMixin
from ..model_base import ModelBase


class CMSPage(ModelBase, IdMixin, TimestampMixin, VersionedMixin):
    __tablename__ = 'cms_pages'

    title:         Mapped[str]  = mapped_column(String(255), nullable=False)
    slug:          Mapped[str]  = mapped_column(String(255), nullable=False, unique=True, index=True)
    content:       Mapped[str]  = mapped_column(Text, nullable=False, default='')
    published:     Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='false')
    template:      Mapped[str]  = mapped_column(String(100), nullable=False, default='default', server_default='default')

    versions = relationship('CMSPageVersion', back_populates='page', cascade='all, delete-orphan', order_by='CMSPageVersion.created_at.desc()')


    def __repr__(self) -> str:
        return f'<CMSPage {self.slug}>'

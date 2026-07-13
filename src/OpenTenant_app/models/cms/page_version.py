from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Text, Integer, ForeignKey
from typing import TYPE_CHECKING

from ..mixins import IdMixin, TimestampMixin, VersionedMixin
from ..model_base import ModelBase
if TYPE_CHECKING:
    from .page import CMSPage


class CMSPageVersion(ModelBase, IdMixin, TimestampMixin, VersionedMixin):
    __tablename__ = 'cms_page_versions'

    content: Mapped[str] = mapped_column(Text, nullable=False)

    page_id: Mapped[int] = mapped_column(Integer, ForeignKey('cms_pages.id', ondelete='CASCADE'), nullable=False, index=True)
    page:    Mapped['CMSPage'] = relationship('CMSPage', back_populates='versions')


    def __repr__(self) -> str:
        return f'<CMSPageVersion page={self.page_id}>'

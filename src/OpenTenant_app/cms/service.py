from sqlalchemy import select
from markupsafe import Markup

from ..models.cms.page_version import CMSPageVersion
from ..models.cms.page import CMSPage
from .renderer import CMSRenderer
from ..extensions import db


class DuplicateSlugError(Exception):
    pass


class CMSService:
    renderer = CMSRenderer()

    ###########################################
    ################# Queries #################
    ###########################################
    def list_pages(self) -> list[CMSPage]:
        stmt = select(CMSPage).order_by(CMSPage.title)
        return db.session.scalars(stmt).all()


    def get_page(self, page_id: int) -> CMSPage|None:
        return db.session.get(CMSPage, page_id)


    def get_by_slug(self, slug: str, published_only: bool=False) -> CMSPage|None:
        stmt = select(CMSPage).where(CMSPage.slug == slug)

        if published_only:
            stmt = stmt.where(CMSPage.published)

        return db.session.scalar(stmt)


    ###########################################
    ################ Rendering ################
    ###########################################
    def render(self, page: CMSPage) -> Markup:
        return self.renderer.render(page.content)


    def preview(self, content: str) -> Markup:
        return self.renderer.render(content)


    ###########################################
    ############## Modifications ##############
    ###########################################
    def create_page(self, title: str, slug: str, content: str, template: str='default') -> CMSPage:
        self.ensure_unique_slug(slug)
        
        page = CMSPage(
            title=title,
            slug=slug,
            content=content,
            template=template
        )

        db.session.add(page)
        db.session.flush()

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return page


    def update_page(self, page: CMSPage, title: str, slug: str, content: str, published: bool, template: str) -> CMSPage:
        if slug != page.slug:
            self.ensure_unique_slug(slug)

        page.title = title
        page.slug = slug
        page.content = content
        page.template = template
        page.published = published

        self.save_version(page)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return page


    def delete_page(self, page: CMSPage) -> None:
        db.session.delete(page)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


    ###########################################
    ############# Helper Functions ############
    ###########################################
    def ensure_unique_slug(self, slug: str) -> None:
        stmt = select(CMSPage).where(CMSPage.slug == slug)

        if db.session.scalar(stmt) is not None:
            raise DuplicateSlugError(f'Slug "{slug}" already exists!')


    def save_version(self, page: CMSPage) -> None:
        version = CMSPageVersion(page=page, content=page.content)

        db.session.add(version)

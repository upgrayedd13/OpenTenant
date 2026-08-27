from typing import Self

from ...extensions import db


class QueryMixin:
    @classmethod
    def get_one_or_none_by(cls, **kwargs) -> Self | None:
        return db.session.execute(db.select(cls).filter_by(**kwargs)).scalar_one_or_none()

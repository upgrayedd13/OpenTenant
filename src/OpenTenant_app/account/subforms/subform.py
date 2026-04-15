from flask_wtf import FlaskForm
from typing import Any


class Subform(FlaskForm):
    class Meta:
        csrf = False

    def disable_editing(self) -> None:
        self.__set_all_render_kw('disabled', True)


    def enable_editing(self) -> None:
        self.__set_all_render_kw('disabled', False)


    def __set_all_render_kw(self, kw: str, val: Any) -> None:
        for field in self._fields.values():
            field.render_kw = field.render_kw or {}
            field.render_kw[kw] = val

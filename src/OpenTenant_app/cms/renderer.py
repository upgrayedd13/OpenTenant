from markupsafe import Markup
import markdown
import bleach

from .allowed_attributes import ALLOWED_ATTRIBUTES
from .allowed_tags import ALLOWED_TAGS


class CMSRenderer:
    DEFAULT_EXTENSIONS = [
        'tables',
        'fenced_code',
        'toc',
        'attr_list',
        'sane_lists'
    ]


    def __init__(self, extensions: list[str]|None=None) -> None:
        self.extensions = extensions or self.DEFAULT_EXTENSIONS
        self.md = markdown.Markdown(extensions=self.extensions)


    def render(self, content: str) -> Markup:
        # prevent maintaining state between conversions
        self.md.reset()

        # convert the markdown to HTML
        html = self.md.convert(content or '')

        # clean the content before returning it
        clean = bleach.clean(
            html,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=['http', 'https', 'mailto'],
            strip=True,
        )

        return Markup(clean)

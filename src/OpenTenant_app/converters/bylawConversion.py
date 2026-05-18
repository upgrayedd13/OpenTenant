from lxml import html as lxml_html
from bs4 import BeautifulSoup
import mammoth
import bleach
import os
import re


ALLOWED_TAGS = [
    "p", "br",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "strong", "em", "b", "i",
    "blockquote", "code", "pre",
    "a",
    "table", "thead", "tbody", "tr", "th", "td",
]


ALLOWED_ATTRS = {
    "a": ["href", "title"],
}


REMOVE_INVALID_CHARS_RE = re.compile(r'[^\w\s-]')
REPLACE_WHITESPACE_RE   = re.compile(r'[\s_-]+')
HEADER_RE               = re.compile(r'^(?P<indent> *)<h(?P<header_num>[234])>(?P<header>.*)</h(?P=header_num)>', re.RegexFlag.MULTILINE)


def slugify(text: str) -> str:
    text = text.lower()                           # convert everything to lowercase
    text = REMOVE_INVALID_CHARS_RE.sub('', text)  # remove everything that isn't a word, whitespace, or dash character
    text = REPLACE_WHITESPACE_RE.sub('-', text)   # replace whitespace, underscores, and dashes as dashes (and collapse multiple to 1)
    return text.strip('-')                        # replace any trailing -


def replace_header_with_header_links(matches: re.Match) -> str:
    indent = matches.group('indent')
    hnum   = matches.group('header_num')
    header = matches.group('header')
    header_id = slugify(header)
    print(f'{indent=}, {hnum=}, {header=}, {header_id=}')

    return (
        f'{indent}<h{hnum} id="{header_id}">\n'
        f'{indent}    {header} <a class="anchor-link" href="#{header_id}">&#182;</a>\n'
        f'{indent}</h{hnum}>'
    )


def add_header_links(html: str) -> str:
    return HEADER_RE.sub(replace_header_with_header_links, html)


def convert(fname_in: str, style_map: str) -> tuple[str, list]:
    with open(fname_in, "rb") as fptr:
        result = mammoth.convert_to_html(fptr, style_map=style_map)
        html = result.value
        messages = result.messages

    tree = lxml_html.fromstring(html)
    pretty_html = lxml_html.tostring(tree, pretty_print=True, encoding='unicode')

    clean_html = bleach.clean(pretty_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, protocols=["http", "https", "mailto"], strip=True)
    clean_html = bleach.linkify(clean_html, callbacks=[bleach.callbacks.nofollow, bleach.callbacks.target_blank])

    final_html = add_header_links(clean_html)

    return final_html, messages


def gen_page(html: str, title: str, css_urls: list[str]|None=None) -> str:
    if css_urls is None:
        css_lines = ''
    else:
        css_lines = ''.join(f'<link rel="stylesheet" href="{{{{ {url} }}}}"\n' for url in css_urls)

    content = (
        '{% extends "base.html" %}\n'
        '\n\n'
        '{% block title %}\n'
        f'{title}\n'
        '{% endblock %}\n'
        '\n\n'
        '{% block extra_css %}\n'
        '<link rel="stylesheet" href="{{ url_for(\'about.static\', filename=\'css/document.css\') }}">\n'
        '<link rel="stylesheet" href="{{ url_for(\'about.static\', filename=\'css/sidebar.css\') }}">\n'
        f'{css_lines}'
        '{% endblock %}\n'
        '\n\n'
        '{% block content %}\n'
        '\n'
        '<div class="doc-layout">\n'
        '    <nav class="doc-toc" id="doc-toc">\n'
        '        <p class="toc-title">Contents</p>\n'
        '        <ul id="toc-list"></ul>\n'
        '    </nav>\n'
        '\n'
        '    <main class="document">\n'
        f'        {html}\n'
        '    </main>\n'
        '</div>\n'
        '\n'
        '<script src="{{ url_for(\'about.static\', filename=\'js/navbar.js\') }}"></script>\n'
        '\n'
        '{% endblock %}\n'
    )

    return content


def main() -> None:
    fpath = '/mnt/c/Users/Upgrayedd/Downloads'
    fname_in = '2025_07_23 Approved LPM Union Bylaws.docx'
    fname_out = 'test.html'
    title = 'Bylaws'

    style_map = """
    p[style-name='Title'] => h1
    p[style-name='Heading 1'] => h2
    p[style-name='Heading 2'] => h3
    """

    content, messages = convert(os.path.join(fpath, fname_in), style_map)
    for message in messages:
        print(f'[{message.type}]: {message.message}')

    page = gen_page(content, title)

    with open(fname_out, 'w') as fptr:
        fptr.write(page)


if __name__ == '__main__':
    main()
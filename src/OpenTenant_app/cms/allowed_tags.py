from bleach import sanitizer

ALLOWED_TAGS = sanitizer.ALLOWED_TAGS | {
    "p",
    "div",
    "span",
    "img",

    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",

    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",

    "pre",
    "code",

    "blockquote",

    "ul",
    "ol",
    "li",

    "hr",

    "br",
}
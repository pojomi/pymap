#!/usr/bin/env python3
import re
from html.parser import HTMLParser
from html import unescape

# Some senders mislabel a part as text/plain while its body is actually (or
# partially) HTML - e.g. a templating bug that dumps the HTML alternative, or
# a leftover "<a href=...>" link, into the plain-text part. Matches a real
# opening/closing/self-closing tag (not just a bare "<" or ">", which can
# appear legitimately in prose like math comparisons).
HTML_TAG_RE = re.compile(
    r'</?[a-zA-Z][a-zA-Z0-9]*'
    r'(?:\s+[a-zA-Z_:][-a-zA-Z0-9_:.]*(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+))?)*'
    r'\s*/?>'
)


def looks_like_html(text: str) -> bool:
    return bool(HTML_TAG_RE.search(text))


# A real link target, as opposed to "#section", "mailto:...", "javascript:...", etc.
ANCHOR_HREF_RE = re.compile(r'(?i)^(https?://|www\.)')


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip: bool = False
        self.anchor_href: str | None = None
        self.anchor_start: int | None = None
        # (start, end) offsets into ''.join(self.parts) marking <a> label text
        # whose href is a real link target - retained verbatim, just colored.
        self.anchor_spans: list[tuple[int, int]] = []

    def _offset(self) -> int:
        return sum(len(p) for p in self.parts)

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in ('script', 'style'):
            self.skip = True
        elif tag == 'br':
            self.parts.append('\n')
        elif tag in ('p', 'div', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.parts.append('\n')
        elif tag == 'a':
            href = next((v for k, v in attrs if k.lower() == 'href' and v), None)
            href = href.strip() if href else None
            if href and ANCHOR_HREF_RE.search(href):
                self.anchor_href = href
                self.anchor_start = self._offset()
            else:
                self.anchor_href = None
                self.anchor_start = None

    def handle_endtag(self, tag: str) -> None:
        if tag in ('script', 'style'):
            self.skip = False
        elif tag in ('p', 'div', 'li'):
            self.parts.append('\n')
        elif tag == 'a':
            if self.anchor_href is not None and self.anchor_start is not None:
                end = self._offset()
                if end > self.anchor_start:
                    self.anchor_spans.append((self.anchor_start, end))
            self.anchor_href = None
            self.anchor_start = None

    def handle_data(self, data: str) -> None:
        if not self.skip:
            # Unescape per chunk (not on the joined text afterwards) so the
            # anchor_spans offsets, computed from these same chunk lengths,
            # stay valid even when an entity's decoded length differs from
            # its source length (e.g. "&#169;" -> "©").
            self.parts.append(unescape(data))


def strip_html(html_text: str) -> tuple[str, list[tuple[int, int]]]:
    extractor = _TextExtractor()
    extractor.feed(html_text)
    raw_text = ''.join(extractor.parts)

    cleaned: list[str] = []
    blank = False
    for line in (ln.strip() for ln in raw_text.splitlines()):
        if line == '':
            if not blank:
                cleaned.append('')
            blank = True
        else:
            cleaned.append(line)
            blank = False
    cleaned_text = '\n'.join(cleaned).strip()

    # The cleanup above only ever removes whitespace - it never reorders or
    # alters the non-whitespace character sequence - so each anchor label's
    # stripped content can be found in document order via a forward search.
    spans: list[tuple[int, int]] = []
    cursor = 0
    for start, end in extractor.anchor_spans:
        label = raw_text[start:end].strip()
        if not label:
            continue
        found = cleaned_text.find(label, cursor)
        if found == -1:
            continue
        spans.append((found, found + len(label)))
        cursor = found + len(label)
    return cleaned_text, spans

#!/usr/bin/env python3
import re
from html.parser import HTMLParser
from html import unescape

<<<<<<< HEAD
=======
# Some senders mislabel a part as text/plain while its body is actually (or
# partially) HTML - e.g. a templating bug that dumps the HTML alternative, or
# a leftover "<a href=...>" link, into the plain-text part. Matches a real
# opening/closing/self-closing tag (not just a bare "<" or ">", which can
# appear legitimately in prose like math comparisons).
>>>>>>> c2892da (rebase local changes on main)
HTML_TAG_RE = re.compile(
    r'</?[a-zA-Z][a-zA-Z0-9]*'
    r'(?:\s+[a-zA-Z_:][-a-zA-Z0-9_:.]*(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+))?)*'
    r'\s*/?>'
)


def looks_like_html(text: str) -> bool:
    return bool(HTML_TAG_RE.search(text))


# A real link target, as opposed to "#section", "mailto:...", "javascript:...", etc.
ANCHOR_HREF_RE = re.compile(r'(?i)^(https?://|www\.)')

<<<<<<< HEAD
COLLAPSIBLE_WHITESPACE_RE = re.compile(r'[ \t\r\n\f\v]+')


def collapse_whitespace(text: str) -> str:
    # Mirrors how a browser renders an HTML text node
    return COLLAPSIBLE_WHITESPACE_RE.sub(' ', text)

=======
>>>>>>> c2892da (rebase local changes on main)

class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip: bool = False
        self.anchor_href: str | None = None
        self.anchor_start: int | None = None
<<<<<<< HEAD
        self.spans: list[tuple[int, int, str]] = []
=======
        # (start, end) offsets into ''.join(self.parts) marking <a> label text
        # whose href is a real link target - retained verbatim, just colored.
        self.anchor_spans: list[tuple[int, int]] = []
>>>>>>> c2892da (rebase local changes on main)

    def _offset(self) -> int:
        return sum(len(p) for p in self.parts)

<<<<<<< HEAD
    def _append(self, text: str, kind: str | None = None) -> None:
        if not text:
            return
        start = self._offset()
        self.parts.append(text)
        if kind:
            self.spans.append((start, start + len(text), kind))

=======
>>>>>>> c2892da (rebase local changes on main)
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
<<<<<<< HEAD
        elif tag == 'img':
            alt = next((v for k, v in attrs if k.lower() == 'alt' and v), None)
            alt = collapse_whitespace(alt).strip() if alt else ''
            placeholder = f'[{alt or "image"}]'
            if self.anchor_href is not None:
                # Inside a real <a href> don't tag this separately so it renders in the link color.
                self._append(placeholder)
            else:
                self._append(placeholder, kind='element')
=======
>>>>>>> c2892da (rebase local changes on main)

    def handle_endtag(self, tag: str) -> None:
        if tag in ('script', 'style'):
            self.skip = False
        elif tag in ('p', 'div', 'li'):
            self.parts.append('\n')
        elif tag == 'a':
            if self.anchor_href is not None and self.anchor_start is not None:
                end = self._offset()
                if end > self.anchor_start:
<<<<<<< HEAD
                    self.spans.append((self.anchor_start, end, 'link'))
=======
                    self.anchor_spans.append((self.anchor_start, end))
>>>>>>> c2892da (rebase local changes on main)
            self.anchor_href = None
            self.anchor_start = None

    def handle_data(self, data: str) -> None:
        if not self.skip:
<<<<<<< HEAD
            # Unescape and collapse insignificant whitespace per chunk
            self.parts.append(collapse_whitespace(unescape(data)))


def _lint_blank_lines_and_seams(raw_text: str) -> tuple[str, list[int | None]]:
    # Second half of the whitespace linter: merges doubled spaces left
    # at chunk boundaries, trims each line's leading/trailing whitespace
    n = len(raw_text)
    pos_map: list[int | None] = [None] * n
    out: list[str] = []

    line_bounds: list[tuple[int, int]] = []
    line_start = 0
    for i, ch in enumerate(raw_text):
        if ch == '\n':
            line_bounds.append((line_start, i))
            line_start = i + 1
    line_bounds.append((line_start, n))

    blank = False
    for start, end in line_bounds:
        i = start
        while i < end and raw_text[i].isspace():
            i += 1
        content_start = i
        j = end
        while j > content_start and raw_text[j - 1].isspace():
            j -= 1
        content_end = j

        survivors: list[int] = []  # raw indices kept, in order
        k = content_start
        while k < content_end:
            if raw_text[k] == ' ':
                run_start = k
                while k < content_end and raw_text[k] == ' ':
                    k += 1
                survivors.append(run_start)  # collapse the run to its first space
            else:
                survivors.append(k)
                k += 1

        if not survivors:
            if blank:
                continue
            blank = True
        else:
            blank = False

        if out:
            out.append('\n')
        base = sum(len(p) for p in out)
        out.append(''.join(raw_text[idx] for idx in survivors))
        for offset, idx in enumerate(survivors):
            pos_map[idx] = base + offset

    joined = ''.join(out)
    front_trim = len(joined) - len(joined.lstrip())
    final = joined.strip()
    adjusted_map: list[int | None] = []
    for p in pos_map:
        if p is not None and front_trim <= p < front_trim + len(final):
            adjusted_map.append(p - front_trim)
        else:
            adjusted_map.append(None)
    return final, adjusted_map


def strip_html(html_text: str) -> tuple[str, list[tuple[int, int, str]]]:
    extractor = _TextExtractor()
    extractor.feed(html_text)
    raw_text = ''.join(extractor.parts)
    cleaned_text, pos_map = _lint_blank_lines_and_seams(raw_text)

    spans: list[tuple[int, int, str]] = []
    for raw_start, raw_end, kind in extractor.spans:
        # Exclude leading/trailing whitespace from the colored range itself
        start = raw_start
        while start < raw_end and raw_text[start].isspace():
            start += 1
        end = raw_end
        while end > start and raw_text[end - 1].isspace():
            end -= 1
        if start >= end:
            continue
        mapped_start = next((pos_map[i] for i in range(start, end) if pos_map[i] is not None), None)
        if mapped_start is None:
            continue
        mapped_end = next((pos_map[i] for i in range(end - 1, start - 1, -1) if pos_map[i] is not None), None)
        if mapped_end is None or mapped_end < mapped_start:
            continue
        spans.append((mapped_start, mapped_end + 1, kind))
=======
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
>>>>>>> c2892da (rebase local changes on main)
    return cleaned_text, spans

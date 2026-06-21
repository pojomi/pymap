#!/usr/bin/env python3
import re
from typing import Callable

URL_RE = re.compile(r'(?:https?://|www\.)\S+', re.IGNORECASE)
URL_WRAPPER_CHARS = '<>[]{}()|'
URL_SENTENCE_PUNCTUATION = '.,;:!?\'"'
PIPE_DIVIDER_RE = re.compile(r'\s*\|\s*')
STRAY_NEWLINE_MARKER_RE = re.compile(r'/n')

Span = tuple[int, int, str]
EditFn = Callable[[str], tuple[str, list[Span]]]


def _apply_outside_spans(text: str, protected: list[Span], edit: EditFn) -> tuple[str, list[Span]]:
    """
    Rebuilds `text`, leaving each `protected` range's content completely
    untouched, and running `edit` on every other (gap) substring. `edit`
    returns (new_gap_text, spans_within_that_new_gap_text). The result is
    the rebuilt text plus one combined, ascending span list covering both
    the untouched protected ranges and any spans `edit` introduced - all
    remapped into the rebuilt text's coordinates.
    """
    pieces: list[str] = []
    spans: list[Span] = []
    pos = 0
    for p_start, p_end, p_kind in sorted(protected, key=lambda s: (s[0], s[1])):
        if p_start < pos:
            continue  # overlapping/out-of-order protected span; skip defensively
        gap_text, gap_spans = edit(text[pos:p_start])
        base = sum(len(p) for p in pieces)
        pieces.append(gap_text)
        spans.extend((base + s, base + e, kind) for s, e, kind in gap_spans)
        protected_base = sum(len(p) for p in pieces)
        pieces.append(text[p_start:p_end])
        spans.append((protected_base, protected_base + (p_end - p_start), p_kind))
        pos = p_end
    gap_text, gap_spans = edit(text[pos:])
    base = sum(len(p) for p in pieces)
    pieces.append(gap_text)
    spans.extend((base + s, base + e, kind) for s, e, kind in gap_spans)
    return ''.join(pieces), spans


def _clean_stray_newline_markers_gap(gap: str) -> tuple[str, list[Span]]:
    # Only convert "/n" outside of URLs
    pieces: list[str] = []
    pos = 0
    for match in URL_RE.finditer(gap):
        pieces.append(STRAY_NEWLINE_MARKER_RE.sub('\n', gap[pos:match.start()]))
        pieces.append(gap[match.start():match.end()])
        pos = match.end()
    pieces.append(STRAY_NEWLINE_MARKER_RE.sub('\n', gap[pos:]))
    return ''.join(pieces), []


def clean_stray_newline_markers(text: str, protected: list[Span] = ()) -> tuple[str, list[Span]]:
    return _apply_outside_spans(text, list(protected), _clean_stray_newline_markers_gap)


def _linkify_gap(gap: str) -> tuple[str, list[Span]]:
    """
    Replaces bare URLs in a gap of text with the word "Link", returning the
    new gap text plus the (start, end, 'link') span of each replacement.
    Some plain-text email generators (e.g. html2text-style converters)
    render an <a href> as "Label (https://...)" - retain the label and
    drop the parenthetical URL entirely in that case, instead.
    """
    gap = PIPE_DIVIDER_RE.sub(' ', gap)
    spans: list[Span] = []
    pieces: list[str] = []
    pos = 0
    search_pos = 0
    while True:
        match = URL_RE.search(gap, search_pos)
        if not match:
            break
        start, end = match.start(), match.end()
        token = gap[start:end]
        # A URL never legitimately contains a wrapper character, so cut the
        # match short at the first one (handles e.g. "http://a.com|http://b.com").
        for i, ch in enumerate(token):
            if ch in URL_WRAPPER_CHARS:
                token = token[:i]
                break
        token = token.rstrip(URL_SENTENCE_PUNCTUATION)
        if not token:
            search_pos = end
            continue
        end = start + len(token)

        if start > pos and gap[start - 1] == '(' and end < len(gap) and gap[end] == ')':
            before = gap[pos:start - 1]
            label = before.strip()
            if label:
                lead = len(before) - len(before.lstrip())
                pieces.append(before[:lead])
                label_start = sum(len(p) for p in pieces)
                pieces.append(label)
                spans.append((label_start, label_start + len(label), 'link'))
                pos = end + 1  # skip past the closing ')'
                search_pos = pos
                continue

        # Drop any wrapper characters immediately preceding the URL
        while start > pos and gap[start - 1] in URL_WRAPPER_CHARS:
            start -= 1
        # Drop any wrapper characters immediately following the URL
        while end < len(gap) and gap[end] in URL_WRAPPER_CHARS:
            end += 1
        pieces.append(gap[pos:start])
        link_start = sum(len(p) for p in pieces)
        pieces.append('Link')
        spans.append((link_start, link_start + 4, 'link'))
        pos = end
        search_pos = end
    pieces.append(gap[pos:])
    return ''.join(pieces), spans


def linkify_line(line: str, protected: list[Span] = ()) -> tuple[str, list[Span]]:
    return _apply_outside_spans(line, list(protected), _linkify_gap)


def split_into_lines(text: str, spans: list[Span]) -> tuple[list[str], list[list[Span]]]:
    # Splits flat, '\n'-joined text (plus its flat spans) into per-line
    # strings and per-line, line-relative spans.
    lines = text.split('\n')
    per_line: list[list[Span]] = [[] for _ in lines]
    starts: list[int] = []
    offset = 0
    for line in lines:
        starts.append(offset)
        offset += len(line) + 1
    for start, end, kind in spans:
        for i, line_start in enumerate(starts):
            line_end = line_start + len(lines[i])
            if line_start <= start <= line_end:
                local_start = start - line_start
                local_end = min(end - line_start, len(lines[i]))
                if local_end > local_start:
                    per_line[i].append((local_start, local_end, kind))
                break
    while len(lines) > 1 and lines[-1] == '':
        lines.pop()
        per_line.pop()
    return lines, per_line


BRACKET_ONLY_RE = re.compile(r'^\[(.+)\]$')
PAREN_URL_ONLY_RE = re.compile(r'^\((?:https?://|www\.)\S+\)$', re.IGNORECASE)


def merge_bracket_image_links(lines: list[str], spans: list[list[Span]]) -> tuple[list[str], list[list[Span]]]:
    new_lines: list[str] = []
    new_spans: list[list[Span]] = []
    i = 0
    n = len(lines)
    while i < n:
        match = BRACKET_ONLY_RE.match(lines[i]) if not spans[i] else None
        if match:
            label = match.group(1)
            # Collapse consecutive duplicate bracket lines (e.g. light/dark image variants)
            j = i + 1
            while j < n and lines[j] == lines[i]:
                j += 1
            k = j
            while k < n and lines[k] == '':
                k += 1
            if k < n and not spans[k] and PAREN_URL_ONLY_RE.match(lines[k]):
                new_lines.append(label)
                new_spans.append([(0, len(label), 'link')])
                i = k + 1  # consume through and including the url line
            else:
                new_lines.append(label)
                new_spans.append([(0, len(label), 'element')])
                i = j
            continue
        new_lines.append(lines[i])
        new_spans.append(spans[i])
        i += 1
    return new_lines, new_spans


def trim_lines(lines: list[str], spans: list[list[Span]]) -> tuple[list[str], list[list[Span]]]:
    trimmed_lines: list[str] = []
    trimmed_spans: list[list[Span]] = []
    blank = False
    for line, line_spans in zip(lines, spans):
        stripped = line.strip()
        if stripped == '':
            if blank:
                continue
            blank = True
        else:
            blank = False
        lead = len(line) - len(line.lstrip())
        new_spans: list[Span] = []
        for start, end, kind in line_spans:
            new_start = max(0, start - lead)
            new_end = min(len(stripped), end - lead)
            if new_end > new_start:
                new_spans.append((new_start, new_end, kind))
        trimmed_lines.append(stripped)
        trimmed_spans.append(new_spans)
    while len(trimmed_lines) > 1 and trimmed_lines[0] == '':
        trimmed_lines.pop(0)
        trimmed_spans.pop(0)
    while len(trimmed_lines) > 1 and trimmed_lines[-1] == '':
        trimmed_lines.pop()
        trimmed_spans.pop()
    return trimmed_lines, trimmed_spans

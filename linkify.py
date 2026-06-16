#!/usr/bin/env python3
import re
from typing import Callable

URL_RE = re.compile(r'(?:https?://|www\.)\S+', re.IGNORECASE)
# Plain-text emails commonly wrap or delimit auto-linked URLs with these
# characters (e.g. "<https://example.com>", "[https://example.com]",
# "http://a.com|http://b.com"). None of them are ever legitimately part of a
# bare URL, so they terminate the match and are dropped from the output
# entirely - both when they precede, are embedded in, or follow the URL.
URL_WRAPPER_CHARS = '<>[]{}()|'
# Legitimate trailing prose punctuation: excluded from the link itself, but
# (unlike wrapper characters) left in place in the surrounding text.
URL_SENTENCE_PUNCTUATION = '.,;:!?\'"'
# Email footers commonly separate links with a bare "|" (e.g.
# "Privacy Policy <link> | Unsubscribe <link>"). It is never meaningful
# prose, so it is collapsed away wherever it appears as its own token.
PIPE_DIVIDER_RE = re.compile(r'\s*\|\s*')
# Some message templates leak a literal "/n" artifact where an actual
# newline was intended (e.g. a template's '\n' escape getting mangled).
STRAY_NEWLINE_MARKER_RE = re.compile(r'/n')

Span = tuple[int, int]
EditFn = Callable[[str], tuple[str, list[Span]]]


def _apply_outside_spans(text: str, protected: list[Span], edit: EditFn) -> tuple[str, list[Span]]:
    # Rebuilds `text`, leaving each `protected` range's content completely
    # untouched, and running `edit` on every other (gap) substring. `edit`
    # returns (new_gap_text, spans_within_that_new_gap_text). The result is
    # the rebuilt text plus one combined, ascending span list covering both
    # the untouched protected ranges and any spans `edit` introduced - all
    # remapped into the rebuilt text's coordinates.
    pieces: list[str] = []
    spans: list[Span] = []
    pos = 0
    for p_start, p_end in sorted(protected):
        if p_start < pos:
            continue  # overlapping/out-of-order protected span; skip defensively
        gap_text, gap_spans = edit(text[pos:p_start])
        base = sum(len(p) for p in pieces)
        pieces.append(gap_text)
        spans.extend((base + s, base + e) for s, e in gap_spans)
        protected_base = sum(len(p) for p in pieces)
        pieces.append(text[p_start:p_end])
        spans.append((protected_base, protected_base + (p_end - p_start)))
        pos = p_end
    gap_text, gap_spans = edit(text[pos:])
    base = sum(len(p) for p in pieces)
    pieces.append(gap_text)
    spans.extend((base + s, base + e) for s, e in gap_spans)
    return ''.join(pieces), spans


def _clean_stray_newline_markers_gap(gap: str) -> tuple[str, list[Span]]:
    # Only convert "/n" outside of URLs, since it's also a common, entirely
    # legitimate URL path segment (e.g. ".../news", ".../notifications").
    pieces: list[str] = []
    pos = 0
    for match in URL_RE.finditer(gap):
        pieces.append(STRAY_NEWLINE_MARKER_RE.sub('\n', gap[pos:match.start()]))
        pieces.append(gap[match.start():match.end()])
        pos = match.end()
    pieces.append(STRAY_NEWLINE_MARKER_RE.sub('\n', gap[pos:]))
    return ''.join(pieces), []


def clean_stray_newline_markers(text: str, protected: list[Span] = ()) -> tuple[str, list[Span]]:
    # `protected` spans (e.g. retained <a> label text) are passed through
    # untouched and are never scanned for "/n" artifacts.
    return _apply_outside_spans(text, list(protected), _clean_stray_newline_markers_gap)


def _linkify_gap(gap: str) -> tuple[str, list[Span]]:
    # Replaces bare URLs in a gap of text with the word "Link", returning the
    # new gap text plus the (start, end) column span of each replacement.
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
        # Drop any wrapper characters immediately preceding the URL
        while start > pos and gap[start - 1] in URL_WRAPPER_CHARS:
            start -= 1
        # Drop any wrapper characters immediately following the URL
        while end < len(gap) and gap[end] in URL_WRAPPER_CHARS:
            end += 1
        pieces.append(gap[pos:start])
        link_start = sum(len(p) for p in pieces)
        pieces.append('Link')
        spans.append((link_start, link_start + 4))
        pos = end
        search_pos = end
    pieces.append(gap[pos:])
    return ''.join(pieces), spans


def linkify_line(line: str, protected: list[Span] = ()) -> tuple[str, list[Span]]:
    # `protected` spans (e.g. retained <a> label text) are kept verbatim -
    # they are never themselves replaced with the word "Link", even if their
    # text happens to look like a URL. The returned spans cover both those
    # passed-through ranges and any new "Link" substitutions, since both are
    # rendered with the same color.
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
    for start, end in spans:
        for i, line_start in enumerate(starts):
            line_end = line_start + len(lines[i])
            if line_start <= start <= line_end:
                local_start = start - line_start
                local_end = min(end - line_start, len(lines[i]))
                if local_end > local_start:
                    per_line[i].append((local_start, local_end))
                break
    while len(lines) > 1 and lines[-1] == '':
        lines.pop()
        per_line.pop()
    return lines, per_line

#!/usr/bin/env python3
from __future__ import annotations
from typing import Any
<<<<<<< HEAD
from typing import cast
=======
>>>>>>> c2892da (rebase local changes on main)
import curses
import re
from os import path, getenv, mkdir, remove
from imaplib import IMAP4_SSL as imap
import socket
from time import sleep
from email import message_from_bytes
<<<<<<< HEAD
from email.message import Message
=======
>>>>>>> c2892da (rebase local changes on main)
from html import unescape

from colors import PALETTE, hex_to_rgb, color
from crypto_utils import crypto_available
from html_utils import strip_html, looks_like_html
<<<<<<< HEAD
from linkify import clean_stray_newline_markers, linkify_line, split_into_lines, trim_lines, merge_bracket_image_links
from imap_utils import parse_mailbox_name, quote_mailbox, fetch_message_headers
from popup import show_popup, prompt_input
from fuzzy_search import fuzzy_score, FUZZY_THRESHOLD
=======
from linkify import clean_stray_newline_markers, linkify_line, split_into_lines
from imap_utils import parse_mailbox_name, quote_mailbox, fetch_message_headers
from popup import show_popup
>>>>>>> c2892da (rebase local changes on main)


class Tty:
    def __init__(self, stdscr: curses.window):
        self.stdscr: curses.window = stdscr
        self.size: tuple[int, int] = self.stdscr.getmaxyx()
        self.center: list[int] = [self.size[0] // 2, self.size[1] // 2]
        self.current_pos: list[int] = []
        self.prev_pos: list[int]
        self.start_pos: list[int]
        curses.use_default_colors()

        self.default_attr: int
        self.ok_attr: int
        self.highlight_attr: int
        self.error_attr: int
        self.success_attr: int
        self.splash_attrs: list[int]
        self.link_attr: int
<<<<<<< HEAD
        self.element_attr: int

        # Default terminal colors (no custom RGB palette redefinition)
        curses.init_pair(1, -1, -1)
        curses.init_pair(2, curses.COLOR_BLUE, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_GREEN, -1)
        curses.init_pair(6, curses.COLOR_RED, -1)
        curses.init_pair(7, curses.COLOR_GREEN, -1)
        curses.init_pair(8, curses.COLOR_YELLOW, -1)
        curses.init_pair(9, curses.COLOR_BLUE, -1)
        curses.init_pair(10, curses.COLOR_MAGENTA, -1)
        curses.init_pair(11, curses.COLOR_CYAN, -1)
        curses.init_pair(12, curses.COLOR_YELLOW, -1)
        self.default_attr = color(1)
        self.ok_attr = color(2)
        self.highlight_attr = curses.A_REVERSE
        self.error_attr = color(4)
        self.success_attr = color(5)
        self.splash_attrs = [color(6), color(7), color(8), color(9), color(10)]
        self.link_attr = color(11) | curses.A_BOLD
        self.element_attr = color(12)
=======

        if curses.can_change_color() and curses.COLORS >= 16:
            for idx, hexval in enumerate(PALETTE):
                try:
                    curses.init_color(idx, *hex_to_rgb(hexval))
                except curses.error:
                    break
            curses.init_pair(1, 7, 8)   # Default
            curses.init_pair(2, 4, 8)   # Ok/Reset buttons
            curses.init_pair(3, 0, 12)  # Highlight
            curses.init_pair(4, 1, 12)  # Error
            curses.init_pair(5, 0, 6)   # Success
            curses.init_pair(6, 1, 8)
            curses.init_pair(7, 2, 8)
            curses.init_pair(8, 3, 8)
            curses.init_pair(9, 4, 8)
            curses.init_pair(10, 5, 8)
            curses.init_pair(11, 4, 8)  # Link text - PALETTE index 4 (#7fbcb4)
            self.default_attr = color(1)
            self.ok_attr = color(2)
            self.highlight_attr = color(3)
            self.error_attr = color(4)
            self.success_attr = color(5)
            self.splash_attrs = [color(6), color(7), color(8), color(9), color(10)]
            self.link_attr = color(11) | curses.A_BOLD
            try:
                self.stdscr.bkgd(' ', self.default_attr)
            except curses.error:
                pass
        else:
            # Fallback for terminals without 16-color / palette redefinition support
            curses.init_pair(1, -1, -1)
            curses.init_pair(2, curses.COLOR_BLUE, -1)
            curses.init_pair(4, curses.COLOR_RED, -1)
            curses.init_pair(5, curses.COLOR_GREEN, -1)
            curses.init_pair(6, curses.COLOR_RED, -1)
            curses.init_pair(7, curses.COLOR_GREEN, -1)
            curses.init_pair(8, curses.COLOR_YELLOW, -1)
            curses.init_pair(9, curses.COLOR_BLUE, -1)
            curses.init_pair(10, curses.COLOR_MAGENTA, -1)
            curses.init_pair(11, curses.COLOR_CYAN, -1)
            self.default_attr = color(1)
            self.ok_attr = color(2)
            self.highlight_attr = curses.A_REVERSE
            self.error_attr = color(4)
            self.success_attr = color(5)
            self.splash_attrs = [color(6), color(7), color(8), color(9), color(10)]
            self.link_attr = color(11) | curses.A_BOLD
>>>>>>> c2892da (rebase local changes on main)

    def intro_print(self, text: str | bytes, attr: int | None = None) -> None:
        if attr is None:
            attr = self.default_attr
        self.stdscr.addstr(self.current_pos[0], self.start_pos[1], f'{text}', attr)
        self.current_pos[0] += 1
        self.stdscr.refresh()

    def safe_addstr(self, win: curses.window, y: int, x: int, text: str, attr: int = 0) -> None:
        maxy, maxx = win.getmaxyx()
        if y < 0 or y >= maxy or x < 0 or x >= maxx:
            return
        available = maxx - x - 1 if maxx - x - 1 > 0 else maxx - x
        text = text[:available]
        if not text:
            return
        try:
            win.addstr(y, x, text, attr)
        except curses.error:
            pass


class Splash:
    def __init__(self, tty: Tty):
        self.tty: Tty = tty
        self.message: list[list[str]] = [
            [
                '███████╗ ',
                '██║  ██║ ',
                '███████╝ ',
                '██║      ',
                '██╝      '],
            [
                '██╗   ██╗ ',
                ' ██╗ ██╔╝ ',
                '  ████╔╝  ',
                '   ██╔╝   ',
                '   ██╝    '],
            [
                '██   ██╗ ',
                '███ ███║ ',
                '██║█ ██║ ',
                '██║  ██║ ',
                '██╝  ██╝ '],
            [
                ' █████╗ ',
                '██║  ██ ',
                '███████ ',
                '██║  ██ ',
                '██╝  ██ '],
            [
                '███████╗ ',
                '██║  ██║ ',
                '███████╝ ',
                '██║      ',
                '██╝      ',]
        ]
        self.rows: int
        self.columns: int
        self.top_margin: int = 1

    def load_pos(self) -> None:
        self.rows = len(self.message[0])
        self.columns = sum(max(len(line) for line in block) for block in self.message)
        self.tty.start_pos = [self.top_margin, max(0, self.tty.center[1] - (self.columns // 2))]
        self.tty.current_pos = [self.tty.start_pos[0], self.tty.start_pos[1]]

    def print_splash(self) -> None:
        for i in range(self.rows):
            self.tty.current_pos[1] = self.tty.start_pos[1]
            for j in range(len(self.message)):
                if j >= len(self.tty.splash_attrs):
                    continue
                self.tty.stdscr.addstr(self.tty.current_pos[0], self.tty.current_pos[1],
                                        self.message[j][i], self.tty.splash_attrs[j])
                self.tty.current_pos[1] += len(self.message[j][i])
            self.tty.current_pos[0] += 1


class Mail:
    def __init__(self, tty: Tty):
        self.tty: Tty = tty
        self.hostname: str
        self.port: int = 993
        self.server: imap
        self.command: str
        self.response: tuple[str, Any]


class Reader:
    def __init__(self, tty: Tty, mail: Mail):
        self.tty: Tty = tty
        self.mail: Mail = mail
        self.lines: list[str] = []
<<<<<<< HEAD
        self.link_spans: list[list[tuple[int, int, str]]] = []
=======
        self.link_spans: list[list[tuple[int, int]]] = []
>>>>>>> c2892da (rebase local changes on main)
        self.top: int = 0
        self.win: curses.window

    def fetch_body(self, msg_id: str) -> None:
        typ, data = self.mail.server.uid('fetch', msg_id, '(RFC822)')
        raw = None
        if typ == 'OK' and data:
            pattern = re.compile(rf'\bUID {re.escape(msg_id)}\b')
            for entry in data:
                if isinstance(entry, tuple) and isinstance(entry[0], bytes) \
                        and pattern.search(entry[0].decode(errors='replace')):
                    raw = entry[1]
                    break
        if not isinstance(raw, bytes):
            self.lines = ['(Unable to retrieve message)']
            return
<<<<<<< HEAD
        msg: Message = message_from_bytes(raw)
        text, anchor_spans = self.extract_text(msg)
        text, spans = clean_stray_newline_markers(text, anchor_spans)
        lines, line_spans = split_into_lines(text, spans)
        lines, line_spans = trim_lines(lines, line_spans)
        lines, line_spans = merge_bracket_image_links(lines, line_spans)
=======
        msg = message_from_bytes(raw)
        text, anchor_spans = self.extract_text(msg)
        text, spans = clean_stray_newline_markers(text, anchor_spans)
        lines, line_spans = split_into_lines(text, spans)
>>>>>>> c2892da (rebase local changes on main)
        self.lines = lines or ['(No content)']
        self.link_spans = line_spans or [[]]
        self.linkify()

    def linkify(self) -> None:
        new_lines = []
        new_spans = []
        for line, protected in zip(self.lines, self.link_spans):
            new_line, line_spans = linkify_line(line, protected)
            new_lines.append(new_line)
            new_spans.append(line_spans)
        self.lines = new_lines
        self.link_spans = new_spans

<<<<<<< HEAD
    def extract_text(self, msg: Message) -> tuple[str, list[tuple[int, int, str]]]:
=======
    def extract_text(self, msg) -> tuple[str, list[tuple[int, int]]]:
>>>>>>> c2892da (rebase local changes on main)
        if msg.is_multipart():
            plain = None
            html_part = None
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                disposition = part.get('Content-Disposition', '')
                if disposition.startswith('attachment'):
                    continue
                ctype = part.get_content_type()
                if ctype == 'text/plain' and plain is None:
                    plain = self.decode_part(part)
                elif ctype == 'text/html' and html_part is None:
                    html_part = self.decode_part(part)
            if plain is not None:
                return strip_html(plain) if looks_like_html(plain) else (unescape(plain), [])
            if html_part is not None:
                return strip_html(html_part)
            return '(No readable content)', []
        else:
            content = self.decode_part(msg)
            if msg.get_content_type() == 'text/html' or looks_like_html(content):
                return strip_html(content)
            return unescape(content), []

    def decode_part(self, part) -> str:
<<<<<<< HEAD
        """Handles Base64 / QP decoding. Returns decoded string."""
=======
        # get_payload(decode=True) handles Base64 / Quoted-Printable transfer encodings
>>>>>>> c2892da (rebase local changes on main)
        payload = part.get_payload(decode=True) or b''
        charset = part.get_content_charset() or 'utf-8'
        try:
            return payload.decode(charset, errors='replace')
        except (LookupError, TypeError):
            return payload.decode('utf-8', errors='replace')

    def run(self) -> None:
        _ = curses.curs_set(0)
        self.tty.stdscr.clear()
        self.tty.stdscr.refresh()
        rows, cols = self.tty.size
        self.win = self.tty.stdscr.derwin(rows, cols, 0, 0)
        max_top = max(0, len(self.lines) - rows)
        while True:
            self.render(rows)
            key = self.tty.stdscr.getch()
            if key in (ord('q'), ord('Q')):
                break
            elif key in (ord('j'), 14, curses.KEY_DOWN):
                if self.top < max_top:
                    self.top += 1
            elif key in (ord('k'), 16, curses.KEY_UP):
                if self.top > 0:
                    self.top -= 1

    def render(self, rows: int) -> None:
        self.win.erase()
        end = min(self.top + rows, len(self.lines))
        for y, idx in enumerate(range(self.top, end)):
            self.render_line(y, self.lines[idx], self.link_spans[idx])
        self.win.refresh()

<<<<<<< HEAD
    def render_line(self, y: int, line: str, spans: list[tuple[int, int, str]]) -> None:
        pos = 0
        for start, end, kind in spans:
            if start > pos:
                self.tty.safe_addstr(self.win, y, pos, line[pos:start])
            attr = self.tty.element_attr if kind == 'element' else self.tty.link_attr
            self.tty.safe_addstr(self.win, y, start, line[start:end], attr)
=======
    def render_line(self, y: int, line: str, spans: list[tuple[int, int]]) -> None:
        pos = 0
        for start, end in spans:
            if start > pos:
                self.tty.safe_addstr(self.win, y, pos, line[pos:start])
            self.tty.safe_addstr(self.win, y, start, line[start:end], self.tty.link_attr)
>>>>>>> c2892da (rebase local changes on main)
            pos = end
        if pos < len(line):
            self.tty.safe_addstr(self.win, y, pos, line[pos:])


class MessageList:
    PAGE_SIZE = 50

    def __init__(self, tty: Tty, mail: Mail, search_criteria: str, sort_desc: bool):
        self.tty: Tty = tty
        self.mail: Mail = mail
        self.search_criteria: str = search_criteria
        self.sort_desc: bool = sort_desc
        self.ids: list[str] = []
        self.messages: list[dict[str, Any]] = []
        self.cursor: int = 0
        self.top: int = 0
        self.win: curses.window
        self.initialized: bool = False
        self.sibling_lists: list['MessageList'] = []

    def ensure_loaded(self) -> None:
        if self.initialized:
            return
        self.initialized = True
        self.fetch_ids()
        self.load_more()

    def fetch_ids(self) -> None:
        typ, data = self.mail.server.uid('search', None, self.search_criteria)
        if typ == 'OK' and data:
            raw = data[0].decode().strip()
            ids = raw.split(' ') if raw else []
            self.ids = list(reversed(ids)) if self.sort_desc else ids

    def remaining(self) -> list[str]:
        return self.ids[len(self.messages):]

    def load_more(self) -> None:
        next_ids = self.remaining()[:self.PAGE_SIZE]
        if not next_ids:
            return
        show_popup(self.tty, 'Loading messages...')
        self.messages.extend(fetch_message_headers(self.mail, next_ids))

    def visible_count(self) -> int:
        rows, _ = self.win.getmaxyx()
        return max(0, rows // 2)

    def move_down(self) -> None:
        if not self.messages:
            return
        if self.cursor == len(self.messages) - 1 and self.remaining():
            self.load_more()
        if self.cursor < len(self.messages) - 1:
            self.cursor += 1
            if self.cursor >= self.top + self.visible_count():
                self.top += 1

    def move_up(self) -> None:
        if not self.messages or self.cursor <= 0:
            return
        self.cursor -= 1
        if self.cursor < self.top:
            self.top -= 1

    def toggle_select(self) -> None:
        if self.messages:
            self.messages[self.cursor]['selected'] = not self.messages[self.cursor]['selected']

    def clamp_cursor(self) -> None:
        if not self.messages:
            self.cursor = 0
            self.top = 0
            return
        if self.cursor >= len(self.messages):
            self.cursor = len(self.messages) - 1
        vis = self.visible_count()
        if self.top > self.cursor:
            self.top = self.cursor
        if self.cursor >= self.top + vis:
            self.top = max(0, self.cursor - vis + 1)

    def render(self) -> None:
        self.win.erase()
        vis = self.visible_count()
        end = min(self.top + vis, len(self.messages))
        for row_idx, msg_idx in enumerate(range(self.top, end)):
            msg = self.messages[msg_idx]
            y = row_idx * 2
<<<<<<< HEAD
            # curses has no true semi-bold attribute - A_BOLD is the closest available
            attr = self.tty.highlight_attr | curses.A_BOLD if msg_idx == self.cursor else self.tty.default_attr
=======
            attr = self.tty.highlight_attr if msg_idx == self.cursor else self.tty.default_attr
>>>>>>> c2892da (rebase local changes on main)
            marker = '*' if msg['selected'] else ' '
            self.tty.safe_addstr(self.win, y, 0, f"{marker}From: {msg['from']}", attr)
            self.tty.safe_addstr(self.win, y + 1, 0, f" Subject: {msg['subject']}", attr)
        if not self.messages:
            self.tty.safe_addstr(self.win, 0, 0, 'No messages', self.tty.default_attr)
        self.win.refresh()
        self.render_modeline()

    def render_modeline(self) -> None:
<<<<<<< HEAD
        rows, cols = self.tty.size
        total = len(self.ids)
        pos = self.cursor + 1 if total else 0
        text = f'({pos} / {total})'
        row = rows - 2  # row rows-1 is the window border's bottom edge
        self.tty.safe_addstr(self.tty.stdscr, row, 1, ' ' * (cols - 2), self.tty.highlight_attr)
        self.tty.safe_addstr(self.tty.stdscr, row, 1, text, self.tty.highlight_attr|curses.A_BOLD)
        self.tty.stdscr.refresh()

=======
        rows, _ = self.tty.size
        total = len(self.ids)
        pos = self.cursor + 1 if total else 0
        text = f'({pos} / {total})'
        self.tty.stdscr.move(rows - 1, 0)
        self.tty.stdscr.clrtoeol()
        self.tty.safe_addstr(self.tty.stdscr, rows - 1, 0, text, self.tty.default_attr)
        self.tty.stdscr.refresh()

    def post_read(self, msg: dict[str, Any]) -> None:
        # Default: message stays visible (e.g. Inbox view shows read mail too)
        pass

>>>>>>> c2892da (rebase local changes on main)
    def open_message(self) -> None:
        if not self.messages:
            return
        msg = self.messages[self.cursor]
        reader = Reader(self.tty, self.mail)
        try:
            reader.fetch_body(msg['id'])
        except self.mail.server.error:
            return
        reader.run()
<<<<<<< HEAD
=======
        self.post_read(msg)
>>>>>>> c2892da (rebase local changes on main)
        self.tty.stdscr.clear()

    def find_archive_mailbox(self) -> str | None:
        try:
            typ, data = self.mail.server.list()
        except self.mail.server.error:
            return None
        if typ != 'OK' or not data:
            return None
        for line in data:
            if not isinstance(line, bytes):
                continue
            decoded = line.decode(errors='replace')
            if '\\Archive' in decoded:
                name = parse_mailbox_name(decoded)
                if name:
                    return name
        for guess in ('Archive', '[Gmail]/All Mail', 'Archives'):
            try:
                typ, _ = self.mail.server.select(quote_mailbox(guess), readonly=True)
                self.mail.server.select()
                if typ == 'OK':
                    return guess
            except self.mail.server.error:
                continue
        return None

    def purge(self, ids: set[str]) -> None:
        self.ids = [i for i in self.ids if i not in ids]
        self.messages = [m for m in self.messages if m['id'] not in ids]
        self.clamp_cursor()

    def purge_everywhere(self, ids: set[str]) -> None:
        self.purge(ids)
        for sibling in self.sibling_lists:
            sibling.purge(ids)
        self.tty.stdscr.clear()

<<<<<<< HEAD
    def refresh_messages(self) -> None:
        """Re-fetches ids and the first page from the server, discarding cached state"""
=======
    def refresh(self) -> None:
        # Re-fetches ids and the first page from the server, discarding cached state
>>>>>>> c2892da (rebase local changes on main)
        self.ids = []
        self.messages = []
        self.cursor = 0
        self.top = 0
        self.initialized = False
        self.ensure_loaded()

    def refresh_everywhere(self) -> None:
<<<<<<< HEAD
        self.refresh_messages()
        for sibling in self.sibling_lists:
            if sibling.initialized:
                sibling.refresh_messages()
=======
        self.refresh()
        for sibling in self.sibling_lists:
            if sibling.initialized:
                sibling.refresh()
>>>>>>> c2892da (rebase local changes on main)
        self.tty.stdscr.clear()

    def delete_selected(self) -> None:
        ids = [m['id'] for m in self.messages if m['selected']]
        if not ids:
            return
        show_popup(self.tty, 'Deleting messages...')
        try:
            self.mail.server.uid('STORE', ','.join(ids), '+FLAGS', '\\Deleted')
            self.mail.server.expunge()
        except self.mail.server.error:
            return
        self.refresh_everywhere()

    def archive_selected(self) -> None:
        ids = [m['id'] for m in self.messages if m['selected']]
        if not ids:
            return
        archive_box = self.find_archive_mailbox()
        if not archive_box:
            return
        show_popup(self.tty, 'Archiving messages...')
        try:
            self.mail.server.uid('COPY', ','.join(ids), quote_mailbox(archive_box))
            self.mail.server.uid('STORE', ','.join(ids), '+FLAGS', '\\Deleted')
            self.mail.server.expunge()
        except self.mail.server.error:
            return
        self.refresh_everywhere()

    def handle_key(self, key: int) -> None:
        match key:
            case _ if key in (ord('j'), 14, curses.KEY_DOWN):
                self.move_down()
            case _ if key in (ord('k'), 16, curses.KEY_UP):
                self.move_up()
            case _ if key == ord(' '):
                self.toggle_select()
            case _ if key in (10, 13, curses.KEY_ENTER):
                self.open_message()
            case _ if key in (ord('d'), ord('D')):
                self.delete_selected()
            case _ if key in (ord('a'), ord('A')):
                self.archive_selected()
            case _:
                pass


class UnreadList(MessageList):
    def __init__(self, tty: Tty, mail: Mail):
        super().__init__(tty, mail, search_criteria='UNSEEN', sort_desc=True)

    def post_read(self, msg: dict[str, Any]) -> None:
        # Once read, the message is no longer "unread" - drop it from this view
        self.purge_everywhere({msg['id']})


class InboxList(MessageList):
    def __init__(self, tty: Tty, mail: Mail):
        super().__init__(tty, mail, search_criteria='ALL', sort_desc=True)


<<<<<<< HEAD
class SearchList(MessageList):
    def __init__(self, tty: Tty, mail: Mail, candidates: list[dict[str, Any]]):
        # Not an IMAP query: a local fuzzy match over messages that have
        # already been retrieved into other tabs (search_criteria is unused).
        super().__init__(tty, mail, search_criteria='', sort_desc=False)
        self.candidates: list[dict[str, Any]] = candidates
        self.query: str = ''
        self.initialized = True
        self.update_query('')

    def update_query(self, query: str) -> None:
        # Re-scores the fixed candidate pool against the latest query text -
        # called on every keystroke while the search box is open, so results
        # populate live as the user types.
        self.query = query
        scored: list[tuple[float, dict[str, Any]]] = []
        if query.strip():
            for msg in self.candidates:
                haystack = f"{msg['from']} {msg['subject']}"
                score = fuzzy_score(query, haystack)
                if score >= FUZZY_THRESHOLD:
                    scored.append((score, msg))
            scored.sort(key=lambda pair: pair[0], reverse=True)
        self.messages = [dict(msg, selected=False) for _, msg in scored]
        self.ids = [m['id'] for m in self.messages]
        self.cursor = 0
        self.top = 0

    def refresh_messages(self) -> None:
        # Search results are a local, point-in-time fuzzy match over
        # already-retrieved messages - there is no live IMAP query to re-run.
        self.cursor = 0
        self.top = 0


=======
>>>>>>> c2892da (rebase local changes on main)
class App:
    def __init__(self, tty: Tty, mail: Mail):
        self.tty: Tty = tty
        self.mail: Mail = mail
        self.order: list[str] = ['Unread', 'Inbox']
        self.tabs: dict[str, MessageList] = {
            'Unread': UnreadList(tty, mail),
            'Inbox': InboxList(tty, mail),
        }
<<<<<<< HEAD
        self._rewire_siblings()
        self.index: int = 0
        # Tab to return to when the Search tab is closed (via Esc or Tab)
        self.previous_tab: str = 'Unread'
=======
        for name in self.order:
            self.tabs[name].sibling_lists = [self.tabs[n] for n in self.order if n != name]
        self.index: int = 0
>>>>>>> c2892da (rebase local changes on main)

    def active(self) -> MessageList:
        return self.tabs[self.order[self.index]]

<<<<<<< HEAD
    def _rewire_siblings(self) -> None:
        for name in self.order:
            self.tabs[name].sibling_lists = [self.tabs[n] for n in self.order if n != name]

    def refresh_all_tabs(self) -> None:
        # Reloads every tab's messages from the server simultaneously,
        # regardless of whether a tab has been visited/initialized yet.
        for tab in self.tabs.values():
            tab.refresh_messages()
        self.tty.stdscr.clear()

    def render_top_bar(self) -> None:
        cols = self.tty.size[1]
        # Row 0 is the window border's top edge, so the tab bar lives on row 1.
        self.tty.safe_addstr(self.tty.stdscr, 1, 1, ' ' * (cols - 2), self.tty.default_attr)
        x = 2
        for i, name in enumerate(self.order):
            label = f' {name} '
            attr = self.tty.highlight_attr if i == self.index else self.tty.default_attr
            self.tty.safe_addstr(self.tty.stdscr, 1, x, label, attr)
            x += len(label) + 1
        self.tty.stdscr.refresh()

    def _collect_search_candidates(self) -> list[dict[str, Any]]:
        # Messages already retrieved into other tabs (deduplicated by id) -
        # the fuzzy search only ever looks at what's already in memory, not
        # whatever else may exist on the server.
        seen: set[str] = set()
        candidates: list[dict[str, Any]] = []
        for name, tab in self.tabs.items():
            if name == 'Search' or not tab.initialized:
                continue
            for msg in tab.messages:
                if msg['id'] not in seen:
                    seen.add(msg['id'])
                    candidates.append(msg)
        return candidates

    def open_search(self) -> None:
        if self.order[self.index] != 'Search':
            self.previous_tab = self.order[self.index]
        candidates = self._collect_search_candidates()
        if 'Search' in self.tabs:
            del self.tabs['Search']
            self.order.remove('Search')
        self.order.append('Search')
        search_list = SearchList(self.tty, self.mail, candidates)
        rows, cols = self.tty.size
        search_list.win = self.tty.stdscr.derwin(rows - 4, cols - 2, 2, 1)
        self.tabs['Search'] = search_list
        self._rewire_siblings()
        self.index = self.order.index('Search')

        def on_change(buf: str) -> None:
            search_list.update_query(buf)
            self.tty.stdscr.border()
            self.render_top_bar()
            search_list.render()

        query = prompt_input(self.tty, 'Search', 'Press Esc to cancel', on_change=on_change)
        self.tty.stdscr.clear()
        if not query:
            # Cancelled, or submitted with no text typed - discard the tab
            # and return to exactly where the user was, with no re-query.
            self.close_search(refresh=False)

    def close_search(self, refresh: bool = True) -> None:
        if 'Search' in self.tabs:
            del self.tabs['Search']
            self.order.remove('Search')
            self._rewire_siblings()
        self.index = self.order.index(self.previous_tab) if self.previous_tab in self.order else 0
        if refresh:
            self.active().refresh_messages()
        self.tty.stdscr.clear()

    def run(self) -> None:
        _ = curses.curs_set(0)
        self.tty.stdscr.clear()
        rows, cols = self.tty.size
        for tab in self.tabs.values():
            tab.win = self.tty.stdscr.derwin(rows - 4, cols - 2, 2, 1)
        self.active().ensure_loaded()
        while True:
            self.tty.stdscr.border()
            self.render_top_bar()
            active = self.active()
            active.render()
            key = self.tty.stdscr.getch()
            if key in (ord('\t'), 27):
                if self.order[self.index] == 'Search':
                    # Esc cancels the search outright (no refresh, returns
                    # to exactly where the user was); Tab still refreshes
                    # the tab being switched to, as elsewhere in the app.
                    self.close_search(refresh=(key == ord('\t')))
                elif key == ord('\t'):
                    self.index = (self.index + 1) % len(self.order)
                    self.tty.stdscr.clear()
                    self.active().refresh_messages()
                continue
            if key in (ord('q'), ord('Q')):
                break
            if key in (ord('r'), ord('R')):
                self.refresh_all_tabs()
                continue
            if key == ord('/'):
                self.open_search()
                continue
=======
    def render_tab_bar(self) -> None:
        self.tty.stdscr.move(0, 0)
        self.tty.stdscr.clrtoeol()
        x = 1
        for i, name in enumerate(self.order):
            label = f' {name} '
            attr = self.tty.highlight_attr if i == self.index else self.tty.default_attr
            self.tty.safe_addstr(self.tty.stdscr, 0, x, label, attr)
            x += len(label) + 1
        self.tty.stdscr.refresh()

    def run(self) -> None:
        _ = curses.curs_set(0)
        self.tty.stdscr.clear()
        self.tty.stdscr.refresh()
        rows, cols = self.tty.size
        for tab in self.tabs.values():
            tab.win = self.tty.stdscr.derwin(rows - 2, cols, 1, 0)
        self.active().ensure_loaded()
        while True:
            self.render_tab_bar()
            active = self.active()
            active.render()
            key = self.tty.stdscr.getch()
            if key == ord('\t'):
                self.index = (self.index + 1) % len(self.order)
                self.tty.stdscr.clear()
                self.active().refresh()
                continue
            if key in (ord('q'), ord('Q')):
                break
>>>>>>> c2892da (rebase local changes on main)
            active.handle_key(key)


class User:
    def __init__(self, tty: Tty, mail: Mail):
        self.tty: Tty = tty
        self.mail: Mail = mail
        self.home: str | None = getenv('HOME')
        self.cfg_dir: str = '.pymap'
<<<<<<< HEAD
        self.cfg_path: str = path.join(cast(str, self.home), self.cfg_dir)
=======
        self.cfg_path: str = path.join(self.home, self.cfg_dir)
>>>>>>> c2892da (rebase local changes on main)
        self.cfg_email: str = path.join(self.cfg_path, '.email')
        self.cfg_pass: str = path.join(self.cfg_path, '.pass')
        self.cfg_token: str = path.join(self.cfg_path, '.token')
        self.email: str
        self.emailenc: bytes
        self.password: str
        self.passenc: bytes
        self.token: bytes

    def init(self) -> None:
        self.check_path()

    def check_path(self) -> None:
        if path.exists(self.cfg_path):
            if crypto_available() and path.exists(self.cfg_email) \
                    and path.exists(self.cfg_pass) and path.exists(self.cfg_token):
                self.tty.intro_print('Found stored credentials. Decrypting')
                if self.handle_decryption():
                    self.define_host()
                    self.imap_connect()
                    self.login()
                    return
                else:
                    remove(self.cfg_email)
                    remove(self.cfg_pass)
                    remove(self.cfg_token)
            self.get_login_creds()
        else:
            mkdir(self.cfg_path)
            self.get_login_creds()

    def get_login_creds(self) -> None:
        self.tty.intro_print('Email: ')
        curses.echo()
        self.email = self.tty.stdscr.getstr().decode()
        _ = curses.curs_set(0)
        curses.noecho()
        self.tty.intro_print('If your account uses 2-Factor Authentication, an App Password')
        self.tty.intro_print('may be required in place of your normal password.')
        self.tty.intro_print('Password: ')
        curses.noecho()
        _ = curses.curs_set(1)
        self.password = self.tty.stdscr.getstr().decode()
        _ = curses.curs_set(0)
        self.define_host()
        self.imap_connect()
        if crypto_available() and self.ask_to_store():
            if self.handle_encryption():
                self.login()
            else:
                self.tty.intro_print('Credentials will not be saved. Continuing to login')
                self.login()
        else:
            self.login()

    def define_host(self) -> None:
        self.mail.hostname = f'imap.{self.email[self.email.find("@") + 1:]}'

    def imap_connect(self) -> None:
        try:
            self.tty.intro_print(f'Connecting to {self.mail.hostname}...')
            self.mail.server = imap(self.mail.hostname, self.mail.port)
        except socket.error as e:
            self.tty.intro_print(f'{e.strerror}', self.tty.error_attr)
            self.tty.intro_print('Exiting')
            sleep(3)
            exit()
        self.tty.intro_print('Connected', self.tty.success_attr)

    def ask_to_store(self) -> bool:
        self.tty.intro_print('Save credentials for automatic login? (y/n): ')
        _ = curses.curs_set(1)
        curses.echo()
        user_response = self.tty.stdscr.getstr().decode().strip().lower()
        _ = curses.curs_set(0)
        curses.noecho()
        if user_response == 'y':
            return True
        elif user_response == 'n':
            self.tty.intro_print('Continuing without storing credentials')
            return False
        else:
            self.tty.intro_print('Invalid entry', self.tty.error_attr)
            return self.ask_to_store()

    def handle_decryption(self) -> bool:
        return self.get_encrypted() and self.decrypt()

    def get_encrypted(self) -> bool:
        try:
            with open(self.cfg_token, 'r') as t:
                self.token = t.read().encode()
            with open(self.cfg_pass, 'r') as p:
                self.passenc = p.read().encode()
            with open(self.cfg_email, 'r') as m:
                self.emailenc = m.read().encode()
        except OSError as e:
            self.tty.intro_print(f'{e.strerror}', self.tty.error_attr)
            self.tty.intro_print('Please login again')
            return False
        return True

    def decrypt(self) -> bool:
        from cryptography.fernet import Fernet
        try:
            fernet = Fernet(self.token)
            self.password = fernet.decrypt(self.passenc).decode()
            self.email = fernet.decrypt(self.emailenc).decode()
        except Exception:
            return False
        return True

    def handle_encryption(self) -> bool:
        self.encrypt()
        return self.store_encrypted_creds()

    def encrypt(self) -> None:
        from cryptography.fernet import Fernet
        self.token = Fernet.generate_key()
        fernet = Fernet(self.token)
        self.emailenc = fernet.encrypt(self.email.encode())
        self.passenc = fernet.encrypt(self.password.encode())

    def store_encrypted_creds(self) -> bool:
        try:
            with open(self.cfg_token, 'w') as t:
                _ = t.write(self.token.decode())
            with open(self.cfg_email, 'w') as mail:
                _ = mail.write(self.emailenc.decode())
            with open(self.cfg_pass, 'w') as pw:
                _ = pw.write(self.passenc.decode())
        except OSError as e:
            self.tty.intro_print(f'{e.strerror}', self.tty.error_attr)
            return False
        self.tty.intro_print(f'Credentials stored in {self.cfg_path}', self.tty.success_attr)
        return True

    def login(self) -> None:
        response = self.mail.server.login(self.email, self.password)
        if response[0] == 'OK':
            self.tty.intro_print('Successfully logged in', self.tty.success_attr)
        else:
            self.tty.intro_print('Failed to login', self.tty.error_attr)
            sleep(2)
            exit()
        response = self.mail.server.select()
        if response[0] != 'OK':
            self.tty.intro_print('Failed to open inbox', self.tty.error_attr)
            sleep(2)
            exit()

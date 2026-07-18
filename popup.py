#!/usr/bin/env python3
from __future__ import annotations
<<<<<<< HEAD
from typing import TYPE_CHECKING, Callable
=======
from typing import TYPE_CHECKING
>>>>>>> c2892da (rebase local changes on main)
import curses

if TYPE_CHECKING:
    from classes import Tty


def show_popup(tty: 'Tty', text: str) -> None:
    # Transient status popup (e.g. "Loading messages...", "Deleting messages...").
    # It is naturally erased by the next full redraw of the underlying windows.
    rows, cols = tty.size
    width = min(cols - 4, max(len(text) + 4, 24)) if cols > 4 else cols
    height = 3
    y = max(0, (rows - height) // 2)
    x = max(0, (cols - width) // 2)
    win = curses.newwin(height, width, y, x)
    win.bkgd(' ', tty.ok_attr)
    win.border()
    tty.safe_addstr(win, 1, max(1, (width - len(text)) // 2), text, tty.ok_attr)
    win.refresh()
<<<<<<< HEAD


def prompt_input(
    tty: 'Tty',
    title: str,
    hint: str,
    on_change: Callable[[str], None] | None = None,
) -> str | None:
    # Centered, bordered text-input popup. Returns the entered text, or None
    # if the user cancels with Esc (or submits an empty/whitespace-only query).
    # If `on_change` is given, it's called with the current buffer once up
    # front and again after every edit - e.g. to live-update a results list
    # in the background while the popup stays on top.
    rows, cols = tty.size
    width = min(cols - 4, 54) if cols > 8 else max(1, cols)
    height = 5
    y = max(0, (rows - height) // 2)
    x = max(0, (cols - width) // 2)
    win = curses.newwin(height, width, y, x)
    win.keypad(True)
    field_y, field_x = 2, 2
    max_len = max(1, width - 4)
    buf = ''

    def redraw_box() -> None:
        win.bkgd(' ', tty.ok_attr)
        win.border()
        tty.safe_addstr(win, 1, 2, title, tty.ok_attr)
        tty.safe_addstr(win, 3, 2, hint, tty.ok_attr)
        tty.safe_addstr(win, field_y, field_x, ' ' * max_len, tty.ok_attr)
        tty.safe_addstr(win, field_y, field_x, buf[-max_len:], tty.ok_attr)
        try:
            win.move(field_y, field_x + min(len(buf), max_len))
        except curses.error:
            pass
        win.refresh()

    _ = curses.curs_set(1)
    try:
        if on_change:
            on_change(buf)
        redraw_box()
        while True:
            key = win.getch()
            if key == 27:  # Esc
                return None
            if key in (10, 13, curses.KEY_ENTER):
                query = buf.strip()
                return query or None
            changed = False
            if key in (curses.KEY_BACKSPACE, 127, 8):
                if buf:
                    buf = buf[:-1]
                    changed = True
            elif 32 <= key < 127:
                buf += chr(key)
                changed = True
            if changed and on_change:
                on_change(buf)
            redraw_box()
    finally:
        _ = curses.curs_set(0)
=======
>>>>>>> c2892da (rebase local changes on main)

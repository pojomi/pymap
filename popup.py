#!/usr/bin/env python3
from __future__ import annotations
from typing import TYPE_CHECKING
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

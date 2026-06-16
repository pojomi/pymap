#!/usr/bin/env python3
import curses

color = curses.color_pair

# Theme palette: index -> hex color. Index 0-7 are the standard ANSI slots,
# 8-15 are their "bright" counterparts.
PALETTE: list[str] = [
    '#2c343a', '#e67c7f', '#a9c181', '#ddbd7f',
    '#7fbcb4', '#d69ab7', '#83c193', '#e7dcc4',
    '#45525c', '#ed9294', '#b0ce7b', '#edc77a',
    '#7ac9c0', '#e5a7c4', '#7dd903', '#b2a790',
]


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(round(c * 1000 / 255) for c in (r, g, b))  # type: ignore[return-value]

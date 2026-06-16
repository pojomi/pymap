#!/usr/bin/env python3
from email.header import decode_header


def decode_mime_words(s: str | None) -> str:
    # Decodes RFC 2047 encoded-words (Base64 / Quoted-Printable) in headers
    if not s:
        return ''
    try:
        parts = decode_header(s)
    except Exception:
        return s
    decoded: list[str] = []
    for text, enc in parts:
        if isinstance(text, bytes):
            try:
                decoded.append(text.decode(enc or 'utf-8', errors='replace'))
            except LookupError:
                decoded.append(text.decode('utf-8', errors='replace'))
        else:
            decoded.append(text)
    return ''.join(decoded).strip()

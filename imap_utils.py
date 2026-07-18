#!/usr/bin/env python3
from __future__ import annotations
from typing import Any, TYPE_CHECKING
import re
from email import message_from_bytes
from email.utils import parseaddr

from mime_utils import decode_mime_words

if TYPE_CHECKING:
    from classes import Mail


def parse_mailbox_name(list_line: str) -> str | None:
    # Parses the mailbox name out of an IMAP LIST response line, e.g.
    # '(\\Archive) "/" "[Gmail]/All Mail"' -> '[Gmail]/All Mail'.
<<<<<<< HEAD
=======
    # The name may be a quoted string (which can contain spaces) or a bare atom.
>>>>>>> c2892da (rebase local changes on main)
    match = re.search(r'"((?:[^"\\]|\\.)*)"\s*$', list_line)
    if match:
        return match.group(1).replace('\\"', '"').replace('\\\\', '\\')
    parts = list_line.rsplit(' ', 1)
    return parts[-1] if parts else None


def quote_mailbox(name: str) -> str:
    # imaplib does not quote command arguments itself, so any mailbox name
    # containing a space or other special character must be quoted here or
    # the server will mis-parse it as multiple arguments.
    if name.startswith('"') and name.endswith('"'):
        return name
    if re.search(r'[\s()"{}\\%*]', name) or not name:
        escaped = name.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return name


def fetch_message_headers(mail: 'Mail', ids: list[str]) -> list[dict[str, Any]]:
    # Fetches From/Subject headers for a batch of UIDs (callers cap batches at 50)
    if not ids:
        return []
    ids_str = ','.join(ids)
    section = '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])'
    typ, data = mail.server.uid('fetch', ids_str, section)
    results: list[dict[str, Any]] = []
    if typ != 'OK' or not data:
        return results
    for msg_id in ids:
        pattern = re.compile(rf'\bUID {re.escape(msg_id)}\b')
        for entry in data:
            if isinstance(entry, tuple) and isinstance(entry[0], bytes) \
                    and pattern.search(entry[0].decode(errors='replace')):
                header_msg = message_from_bytes(entry[1])
<<<<<<< HEAD
                from_header = header_msg.get('From', '')
                realname, addr = parseaddr(from_header)
                display_name = decode_mime_words(realname).strip()
                from_display = display_name or addr or from_header
=======
                from_addr = parseaddr(header_msg.get('From', ''))[1] or header_msg.get('From', '')
>>>>>>> c2892da (rebase local changes on main)
                subject = decode_mime_words(header_msg.get('Subject'))
                if not subject:
                    subject = 'None'
                results.append({
                    'id': msg_id,
<<<<<<< HEAD
                    'from': from_display,
=======
                    'from': from_addr,
>>>>>>> c2892da (rebase local changes on main)
                    'subject': subject,
                    'selected': False,
                })
                break
    return results

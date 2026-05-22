#!/usr/bin/env python3
"""Candump-ish line parsing shared by tooling scripts."""

from __future__ import annotations

import re


LINE_RE = re.compile(
    r"""
    \(\s*(?P<ts>[0-9.]+)\s*\)\s+      # (timestamp)
    (?:[^\s]+\s+)?                     # optional interface name like can0
    (?P<id>(?:0x)?[0-9A-Fa-f]{1,8})    # CAN id hex (optional 0x prefix)
    \#\s*(?P<data>[0-9A-Fa-f]*)        # hex payload after #
    """,
    re.VERBOSE,
)


def parse_line(line: str) -> tuple[float, int, bytes] | None:
    raw = line.strip()
    if not raw or raw.startswith("#"):
        return None
    m = LINE_RE.search(raw)
    if not m:
        return None
    ts = float(m.group("ts"))
    id_txt = m.group("id").lower().removeprefix("0x")
    can_id = int(id_txt, 16)
    data_hex = m.group("data") or ""
    if len(data_hex) % 2:
        data_hex = data_hex[:-1]
    data = bytes.fromhex(data_hex) if data_hex else b""
    return ts, can_id, data

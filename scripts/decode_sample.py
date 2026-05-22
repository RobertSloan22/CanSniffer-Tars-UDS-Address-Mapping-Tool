#!/usr/bin/env python3
"""
Decode candump-ish lines with a Vector DBC (cantools).

Example line formats supported (regex flexible):
  (123.456789) can0 123#DEADBEEF
  123.456789 0x123#DEAFF00D
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cantools

from candump_parse import parse_line


def decode_file(dbc_path: Path, candump_path: Path, extended: bool) -> None:
    db = cantools.database.load_file(str(dbc_path))
    decoded_rows: list[tuple[float, str, str]] = []

    for line in candump_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parsed = parse_line(line)
        if parsed is None:
            continue
        ts, can_id, data = parsed

        arb_id = can_id
        msg = None
        if extended:
            try:
                msg = db.get_message_by_frame_id(arb_id)
            except KeyError:
                msg = None
        else:
            for cand in (arb_id & 0x7FF, arb_id & 0x1FFFFFFF, arb_id):
                try:
                    msg = db.get_message_by_frame_id(cand)
                    break
                except KeyError:
                    continue

        if msg is None:
            continue

        try:
            signals = msg.decode(data, decode_choices=True)
            for name, val in signals.items():
                decoded_rows.append((ts, f"{msg.name}.{name}", str(val)))
        except Exception:
            decoded_rows.append((ts, msg.name, f"<decode error len={len(data)}>"))

    if not decoded_rows:
        print("No frames matched this DBC. Check IDs (extended vs standard) and candump export format.")
        return

    for ts, key, val in decoded_rows[:500]:
        print(f"{ts:12.6f}  {key:40}  {val}")

    remaining = len(decoded_rows) - 500
    if remaining > 0:
        print(f"... suppressed {remaining} additional decoded rows")


def main() -> None:
    p = argparse.ArgumentParser(description="Decode candump-style log with cantools + DBC")
    p.add_argument("dbc", type=Path, help="path to .dbc")
    p.add_argument("log", type=Path, help="path to candump-ish .txt/.log export")
    p.add_argument(
        "--extended",
        action="store_true",
        help="Use extended-ID lookup only first",
    )
    args = p.parse_args()
    decode_file(args.dbc, args.log, args.extended)


if __name__ == "__main__":
    main()

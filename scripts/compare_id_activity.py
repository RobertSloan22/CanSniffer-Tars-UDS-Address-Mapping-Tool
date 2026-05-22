#!/usr/bin/env python3
"""
Compare per-CAN-ID frame counts between two candump-ish exports (baseline vs stimulus).
Prioritizes IDs whose traffic changes between logs (ECU mapping aid).
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from candump_parse import parse_line


def collect_ids(path: Path) -> Counter[int]:
    counts: Counter[int] = Counter()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parsed = parse_line(line)
        if parsed is None:
            continue
        _, can_id, _ = parsed
        counts[can_id] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare CAN-ID frame counts between baseline and stimulus candump-ish logs"
    )
    parser.add_argument("baseline", type=Path, help="candump-ish log before stimulus")
    parser.add_argument("stimulus", type=Path, help="candump-ish log during/after stimulus")
    args = parser.parse_args()

    baseline = collect_ids(args.baseline)
    stimulus = collect_ids(args.stimulus)
    ids = sorted(set(baseline.keys()) | set(stimulus.keys()))

    rows: list[tuple[int, int, int, int]] = []
    for can_id in ids:
        ba = baseline.get(can_id, 0)
        st = stimulus.get(can_id, 0)
        rows.append((st - ba, st, ba, can_id))

    rows.sort(key=lambda r: abs(r[0]), reverse=True)

    print("sorted by |stimulus - baseline| frame count delta\n")
    print(f"{'delta':>8}  {'baseline':>10}  {'stimulus':>10}   can_id_hex")
    for delta, st, ba, can_id in rows[:150]:
        print(f"{delta:8d}  {ba:10d}  {st:10d}   {can_id:#x}")


if __name__ == "__main__":
    main()

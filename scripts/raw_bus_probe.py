"""Minimal python-can probe: open the PCAN bus, print whatever arrives.

Used to isolate hardware/cable/wiring issues from Flask app issues. If this
prints frames but the web UI does not, the bug is in our app. If neither
prints frames, the bus is silent from the adapter's view (cable, pinout,
vehicle state) regardless of our app.

Usage (PowerShell from repo root, with venv active):
    .\.venv\Scripts\python.exe scripts\raw_bus_probe.py
Press Ctrl+C to stop.
"""

from __future__ import annotations

import can
import time

CHANNEL = "PCAN_USBBUS1"
BITRATES = (500_000, 250_000, 125_000, 1_000_000, 33_333, 83_333, 95_238)
PROBE_SECONDS = 4


def probe(bitrate: int) -> tuple[int, int, str]:
    """Open the bus at `bitrate`, read for PROBE_SECONDS, return (count, unique, state_str)."""
    try:
        bus = can.Bus(
            interface="pcan",
            channel=CHANNEL,
            bitrate=bitrate,
            state=can.BusState.PASSIVE,
            receive_own_messages=False,
        )
    except Exception as e:
        return (0, 0, f"OPEN FAIL: {e}")

    count = 0
    ids: set[int] = set()
    sample_lines: list[str] = []
    deadline = time.monotonic() + PROBE_SECONDS
    while time.monotonic() < deadline:
        msg = bus.recv(timeout=0.2)
        if msg is None:
            continue
        count += 1
        ids.add(msg.arbitration_id)
        if len(sample_lines) < 3:
            sample_lines.append(
                f"      ts={msg.timestamp:.3f}  id=0x{msg.arbitration_id:X}  "
                f"ext={int(msg.is_extended_id)}  dlc={msg.dlc}  "
                f"data={msg.data.hex().upper()}"
            )

    state_str = "?"
    try:
        state_str = str(bus.state).replace("BusState.", "")
    except Exception:
        pass
    bus.shutdown()
    if sample_lines:
        print("\n".join(sample_lines))
    return count, len(ids), state_str


print(f"Probing {CHANNEL} across {len(BITRATES)} standard bitrates "
      f"({PROBE_SECONDS}s each, listen-only)...\n")
print(f"{'bitrate':>10}  {'frames':>7}  {'uniq':>5}  state")
print("-" * 60)
any_traffic = False
for br in BITRATES:
    count, unique, state = probe(br)
    flag = "  <-- TRAFFIC!" if count > 0 else ""
    if count > 0:
        any_traffic = True
    print(f"{br:>10}  {count:>7}  {unique:>5}  {state}{flag}")

if not any_traffic:
    print(
        "\nNo traffic at any standard bitrate. Likely causes (in order):\n"
        "  1. OBD-II cable is NOT wired for HS-CAN on pins 6/14 (verify\n"
        "     with multimeter: continuity between OBD-II pin 6 -> DB-9 pin 7,\n"
        "     and OBD-II pin 14 -> DB-9 pin 2). Many cheap 'OBD-II cables'\n"
        "     are K-line / ISO 9141 only.\n"
        "  2. CAN_H and CAN_L swapped on the cable.\n"
        "  3. Adapter termination ON + vehicle bus terminated = bus loaded\n"
        "     too low to drive recessive bits reliably (TER LED solid means\n"
        "     the adapter's 120ohm is engaged; disable in PCAN-View).\n"
        "  4. DB-9 not fully seated on the adapter (push hard, screw down).\n"
        "  5. Open PCAN-View (PEAK GUI tool) and connect manually -- it\n"
        "     shows bus error counters and is the gold-standard diagnostic."
    )

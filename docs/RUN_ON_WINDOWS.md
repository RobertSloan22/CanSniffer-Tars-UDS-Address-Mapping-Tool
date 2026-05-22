# Run the live monitor on Windows

This is the canonical setup for the **live monitoring UI** (`web/app.py`). The
adapter is a PEAK PCAN-USB; it speaks via PEAK's PCAN-Basic driver, so the app
runs on Windows where the driver is installed. No usbipd, no SocketCAN, no WSL.

## Prerequisites (one-time)

1. **Python 3.11+** on PATH (`python --version`) — install from python.org with
   "Add to PATH" or use the Windows `py` launcher. See
   [PYTHON_OPTIONAL_WINDOWS.md](PYTHON_OPTIONAL_WINDOWS.md).
2. **PEAK PCAN-Basic driver** — download from
   <https://www.peak-system.com/quick/DrvSetup> (free, English). Install the
   "PCAN-Basic API" component. This places `PCANBasic.dll` somewhere
   `python-can` can find it. Reboot if prompted.
3. **Adapter plugged into a USB port** on the Windows machine. Verify in
   Device Manager → "CAN Hardware" → PEAK PCAN-USB FD (or similar).

## Project setup (one-time)

```powershell
cd C:\Users\rstec\cansniffer
.\scripts\install_python_tools.ps1
```

This creates `.venv\` in the repo root and installs everything from
`requirements.txt` (`python-can`, `cantools`, `pandas`, `matplotlib`, `flask`).

## Launch

```powershell
cd C:\Users\rstec\cansniffer
.\.venv\Scripts\python.exe -m web.app
```

Open <http://localhost:8000> in a browser. Pick **Channel** (default
`PCAN_USBBUS1` = first PEAK USB device) and **Bitrate** (most HS-CAN buses are
500 kbit/s), then click **Start**.

## What to expect

- Frames stream live in the right pane (newest first).
- The "Top IDs" panel ranks IDs by frame count — useful for finding the
  highest-traffic ECUs first.
- **Save session to captures/** dumps the in-memory frame buffer as a
  candump-style text file you can feed to `scripts/decode_sample.py` or
  `scripts/compare_id_activity.py` (also exposed via the **Decode** and **ID
  counts** buttons at the bottom).

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Start button reports `OSError: ...PCANBasic.dll` | PCAN-Basic driver not installed — do step 2 above. |
| Start reports `PcanCanInitializationError: PCAN_ERROR_INITIALIZE` | Wrong channel selected, adapter unplugged, or another app (SavvyCAN) is holding it open. Close SavvyCAN. |
| Start reports `PCAN_ERROR_REGTEST` or hangs | Bitrate mismatch with the bus. Try 250k or 125k. |
| No frames after Start | Bus is silent OR adapter wired incorrectly (CAN-H/CAN-L swapped, no termination). Run SavvyCAN once to sanity-check the wiring. |
| Browser shows "error" pill | Click the pill; the red banner at top has the python-can error message verbatim. |

## What's removed

Earlier builds shipped a synthetic-frame **SimulatorSource** for UI testing
without hardware. That is gone. The only source is `PcanSource`. If a future
adapter requires a different backend (Kvaser, slcan, SocketCAN), add a new
`*Source` class in `web/sources.py` matching the same `start()`/`stop()`
interface and select it in `web/app.py`.

# Python decoding pipeline

Depends on **`requirements.txt`** at repo root (`python-can`, `cantools`, `pandas`, `matplotlib`).

## Install

From repo root (see [PYTHON_OPTIONAL_WINDOWS.md](../docs/PYTHON_OPTIONAL_WINDOWS.md)):

```powershell
.\scripts\install_python_tools.ps1
.\.venv\Scripts\Activate.ps1
```

## Scripts

| Script | Purpose |
|--------|---------|
| `decode_sample.py` | Decode a **candump-style** `.txt` export using your `.dbc`. |
| `compare_id_activity.py` | Diff **ID-level frame counts** between baseline vs stimulus logs. |

## Export format from SavvyCAN

SavvyCAN can export traces to ASCII formats depending on version. For these scripts:

- Prefer **ASCII / candump-like** exports with lines like `(0.012345) 123 #DEADBEEF` or similar.
- If your export differs, preprocess to one line per frame: `RELATIVE_SECONDS CAN_ID HEXDATA` (classic CAN hex; FD may need preprocessing—normalize with SavvyCAN or custom script).

Place raw exports under `captures/` (gitignored extensions—keep local).

## Interfaces (future live sniff)

Your Pibiger path on Windows typically goes through SavvyCAN, not necessarily `python-can` USB directly. Use **file ingest** here first; plug in SocketCAN/`python-can` on Linux once `can0` exists per vendor SocketCAN docs.

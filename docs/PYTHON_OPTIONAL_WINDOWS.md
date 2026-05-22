# Optional: Bootstrap Python tooling (Windows)

If `python`, `pip`, or `py` does not resolve in PowerShell:

1. Install **[Python 3.11+](https://www.python.org/downloads/windows/)**, check **“Add python.exe to PATH”**.
2. Reopen terminal, then from repo root:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
.\scripts\install_python_tools.ps1
```

This creates `.venv/` and installs `requirements.txt`.

## Smoke test

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\decode_sample.py templates\minimal_example.dbc templates\sample_candump.txt
python scripts\compare_id_activity.py templates\sample_candump.txt templates\sample_candump.txt
```

The compare script prints zero deltas when both files match.

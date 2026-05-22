# CANsniffer — Pibiger SavvyCAN-FD tooling

Workspace support for **[CAN/CAN-FD Setup Plan](https://docs.pibiger-tech.com/home/usb-to-can-fd-series/savvycanfd/quick-start-guide)** workflows: SavvyCAN + optional Python decoding.

## Quick start

1. **Windows install** — Follow [docs/SETUP_WINDOWS.md](docs/SETUP_WINDOWS.md) (driver, SavvyCAN, verification).
2. **Live monitor (browser UI)** — Follow [docs/RUN_ON_WINDOWS.md](docs/RUN_ON_WINDOWS.md): install PEAK PCAN-Basic driver, run `install_python_tools.ps1`, launch `python -m web.app`, open <http://localhost:8000>.
3. **Passive sniffing** — Use [docs/PASSIVE_CAPTURE_CHECKLIST.md](docs/PASSIVE_CAPTURE_CHECKLIST.md) before attaching to a live bus.
4. **ECU mapping** — Fill [templates/capture_matrix.csv](templates/capture_matrix.csv) and [docs/ECU_MAPPING_WORKFLOW.md](docs/ECU_MAPPING_WORKFLOW.md).
5. **Python pipeline** — See [scripts/README.md](scripts/README.md) (Phase 5 checks: [VALIDATION_AND_GUARDRAILS.md](docs/VALIDATION_AND_GUARDRAILS.md)).
6. **Optional Linux** — [docs/LINUX_SOCKETCAN_TOOLS.md](docs/LINUX_SOCKETCAN_TOOLS.md) (`can-utils`, SocketCAN).

Requires **Python 3.11+** on PATH (`python`) or Windows **py** launcher — see [docs/PYTHON_OPTIONAL_WINDOWS.md](docs/PYTHON_OPTIONAL_WINDOWS.md).

```powershell
cd C:\Users\rstec\cansniffer
.\scripts\install_python_tools.ps1
.\.venv\Scripts\Activate.ps1
python scripts\decode_sample.py templates\minimal_example.dbc templates\sample_candump.txt
```

## Project layout

| Path | Purpose |
|------|---------|
| `docs/SETUP_WINDOWS.md` | Driver + SavvyCAN + Device Manager checks |
| `docs/PASSIVE_CAPTURE_CHECKLIST.md` | Listen-only, wiring, termination, baseline |
| `docs/ECU_MAPPING_WORKFLOW.md` | Controlled sessions + SavvyCAN tips |
| `docs/LINUX_SOCKETCAN_TOOLS.md` | Optional Phase 4: `can-utils`, SocketCAN, WSL caveat |
| `docs/VALIDATION_AND_GUARDRAILS.md` | Phase 5: log quality, DBC versioning, injection policy |
| `docs/PYTHON_OPTIONAL_WINDOWS.md` | Python `venv` + smoke test |
| `templates/capture_matrix.csv` | Test matrix template |
| `requirements.txt` | `python-can`, `cantools`, `pandas`, `matplotlib`, `flask` |
| `scripts/` | Log helpers and DBC decode examples |
| `web/` | Browser monitor app (Flask + SSE, PEAK PCAN-USB live source) |

## External references

- [Pibiger SavvyCAN-FD Quick Start](https://docs.pibiger-tech.com/home/usb-to-can-fd-series/savvycanfd/quick-start-guide)
- [SavvyCAN releases](https://github.com/collin80/SavvyCAN/releases)
- [SavvyCAN connection docs](https://savvycan.com/docs/connectionwindow.html)

## Legal / safety

Only sniff or interact with buses you **own** or have **written authorization** to access. Passive listen-only reduces risk but does not remove liability.
# CanSniffer-Tars-UDS-Address-Mapping-Tool

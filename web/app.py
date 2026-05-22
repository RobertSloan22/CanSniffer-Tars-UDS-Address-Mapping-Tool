"""Flask app — operator UI for CANsniffer.

Run from repo root on Windows:
    .\.venv\Scripts\python.exe -m web.app
Then open http://localhost:8000

Requires PEAK PCAN-Basic driver (PCAN-Basic.dll) installed system-wide on
Windows, and the PCAN-USB adapter connected. No simulator fallback.
"""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

from web.sources import FrameBus, PcanSource

REPO_ROOT = Path(__file__).resolve().parent.parent
CAPTURES_DIR = REPO_ROOT / "captures"
SCRIPTS_DIR = REPO_ROOT / "scripts"

DEFAULT_CHANNEL = "PCAN_USBBUS1"
DEFAULT_BITRATE = 500_000
ALLOWED_BITRATES = (125_000, 250_000, 500_000, 1_000_000)

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))

bus = FrameBus()
_state_lock = threading.Lock()
_source: PcanSource | None = None
_last_error: str | None = None


def _running() -> bool:
    return _source is not None


def _list_captures() -> list[str]:
    if not CAPTURES_DIR.exists():
        return []
    exts = {".txt", ".log", ".asc", ".savvylog"}
    return sorted(
        p.name for p in CAPTURES_DIR.iterdir() if p.is_file() and p.suffix.lower() in exts
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    snap = bus.snapshot()
    snap["running"] = _running()
    snap["captures"] = _list_captures()
    snap["channel"] = _source.channel if _source else DEFAULT_CHANNEL
    snap["bitrate"] = _source.bitrate if _source else DEFAULT_BITRATE
    snap["listen_only"] = _source.listen_only if _source else True
    runtime_err = _source.error if _source else None
    snap["error"] = runtime_err or _last_error
    return jsonify(snap)


@app.route("/api/start", methods=["POST"])
def api_start():
    global _source, _last_error
    payload = request.get_json(silent=True) or {}
    channel = str(payload.get("channel") or DEFAULT_CHANNEL)
    try:
        bitrate = int(payload.get("bitrate") or DEFAULT_BITRATE)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "msg": "bitrate must be an integer"}), 400
    if bitrate not in ALLOWED_BITRATES:
        return jsonify(
            {"ok": False, "msg": f"bitrate must be one of {ALLOWED_BITRATES}"}
        ), 400
    listen_only = payload.get("listen_only", True)
    if isinstance(listen_only, str):
        listen_only = listen_only.lower() not in ("false", "0", "no", "off")
    listen_only = bool(listen_only)

    with _state_lock:
        if _source is not None:
            return jsonify({"ok": False, "msg": "already running"})
        bus.reset()
        src = PcanSource(bus, channel=channel, bitrate=bitrate, listen_only=listen_only)
        try:
            src.start()
        except Exception as e:
            _last_error = f"{type(e).__name__}: {e}"
            return jsonify({"ok": False, "msg": _last_error}), 500
        _last_error = None
        _source = src
    return jsonify(
        {"ok": True, "channel": channel, "bitrate": bitrate, "listen_only": listen_only}
    )


@app.route("/api/stop", methods=["POST"])
def api_stop():
    global _source
    with _state_lock:
        if _source is None:
            return jsonify({"ok": False, "msg": "not running"})
        _source.stop()
        _source = None
    return jsonify({"ok": True})


@app.route("/api/stream")
def api_stream():
    q = bus.subscribe()

    def gen():
        try:
            while True:
                try:
                    frame = q.get(timeout=10)
                    yield f"data: {json.dumps(frame)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            bus.unsubscribe(q)

    return Response(gen(), mimetype="text/event-stream")


@app.route("/api/save_session", methods=["POST"])
def api_save_session():
    text = bus.session_text()
    if not text.strip():
        return jsonify({"ok": False, "msg": "no frames in session"})
    CAPTURES_DIR.mkdir(exist_ok=True)
    fname = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    (CAPTURES_DIR / fname).write_text(text, encoding="utf-8")
    return jsonify({"ok": True, "filename": fname})


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    capture = data.get("capture")
    dbc = data.get("dbc", "templates/minimal_example.dbc")
    mode = data.get("mode", "decode")

    if not capture:
        return jsonify({"ok": False, "msg": "no capture selected"})

    cap_path = CAPTURES_DIR / capture
    if not cap_path.exists():
        return jsonify({"ok": False, "msg": f"missing capture: {capture}"})

    if mode == "decode":
        dbc_path = (REPO_ROOT / dbc).resolve()
        if not dbc_path.exists():
            return jsonify({"ok": False, "msg": f"missing dbc: {dbc}"})
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "decode_sample.py"),
            str(dbc_path),
            str(cap_path),
        ]
    elif mode == "ids":
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "compare_id_activity.py"),
            str(cap_path),
            str(cap_path),
        ]
    else:
        return jsonify({"ok": False, "msg": f"unknown mode: {mode}"})

    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, cwd=str(REPO_ROOT)
        )
        return jsonify(
            {
                "ok": out.returncode == 0,
                "output": (out.stdout or "") + (out.stderr or ""),
                "cmd": " ".join(cmd),
            }
        )
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "msg": "analysis timed out"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True, debug=False)

"""Frame sources + central bus.

FrameBus = single fan-out hub: a source publishes frames; subscribers (SSE
clients) read them via per-client queues. Stats and a recent-frames ring are
maintained centrally so the UI keeps working even when no client is attached.

PcanSource = live python-can listener bound to a PEAK PCAN-USB adapter.
Requires PEAK's PCAN-Basic driver (PCAN-Basic.dll on Windows). Default channel
PCAN_USBBUS1 is the first PEAK USB device on the host.
"""

from __future__ import annotations

import queue
import threading
import time
from collections import defaultdict, deque
from typing import Any

import can


class FrameBus:
    def __init__(self, recent_limit: int = 200) -> None:
        self._lock = threading.Lock()
        self.frame_count: int = 0
        self.id_counts: dict[int, int] = defaultdict(int)
        self.recent: deque[dict[str, Any]] = deque(maxlen=recent_limit)
        self._subscribers: list[queue.Queue] = []
        self.session_lines: list[str] = []

    def publish(self, frame: dict[str, Any]) -> None:
        line = f"({frame['ts']:.6f}) pcan {frame['id']:X}#{frame['data']}\n"
        with self._lock:
            self.frame_count += 1
            self.id_counts[frame["id"]] += 1
            self.recent.append(frame)
            self.session_lines.append(line)
            subs = list(self._subscribers)
        for q in subs:
            try:
                q.put_nowait(frame)
            except queue.Full:
                pass

    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=500)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            top = sorted(self.id_counts.items(), key=lambda kv: -kv[1])[:20]
            return {
                "frame_count": self.frame_count,
                "unique_ids": len(self.id_counts),
                "top_ids": [(f"0x{cid:X}", n) for cid, n in top],
            }

    def reset(self) -> None:
        with self._lock:
            self.frame_count = 0
            self.id_counts.clear()
            self.recent.clear()
            self.session_lines.clear()

    def session_text(self) -> str:
        with self._lock:
            return "".join(self.session_lines)


class PcanSource:
    """python-can listener for PEAK PCAN-USB adapters via PCAN-Basic.

    On start() the adapter is opened in listen-only mode (no transmissions on
    the bus). Failures (driver missing, device not present, bus init error)
    raise from start() so callers can surface them to the operator.
    """

    def __init__(
        self,
        bus_obj: FrameBus,
        channel: str = "PCAN_USBBUS1",
        bitrate: int = 500_000,
        listen_only: bool = True,
    ) -> None:
        self._fb = bus_obj
        self._channel = channel
        self._bitrate = int(bitrate)
        self._listen_only = bool(listen_only)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._can_bus: can.BusABC | None = None
        self._error: str | None = None

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def bitrate(self) -> int:
        return self._bitrate

    @property
    def listen_only(self) -> bool:
        return self._listen_only

    @property
    def error(self) -> str | None:
        return self._error

    def start(self) -> None:
        self._error = None
        # PASSIVE = adapter does not ACK or transmit. Safe to attach to a live
        # vehicle bus without risk of perturbing ECUs. ACTIVE is required when
        # we want to send UDS requests / OBD-II PID polls.
        state = can.BusState.PASSIVE if self._listen_only else can.BusState.ACTIVE
        self._can_bus = can.Bus(
            interface="pcan",
            channel=self._channel,
            bitrate=self._bitrate,
            state=state,
            receive_own_messages=False,
        )
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
        if self._can_bus is not None:
            try:
                self._can_bus.shutdown()
            except Exception:
                pass
            self._can_bus = None

    def _run(self) -> None:
        t0 = time.monotonic()
        bus = self._can_bus
        if bus is None:
            self._error = "bus not initialized"
            return
        while not self._stop.is_set():
            try:
                msg = bus.recv(timeout=0.25)
            except can.CanError as e:
                self._error = f"CanError: {e}"
                break
            except Exception as e:
                self._error = f"{type(e).__name__}: {e}"
                break
            if msg is None:
                continue
            self._fb.publish(
                {
                    "ts": round(time.monotonic() - t0, 6),
                    "id": int(msg.arbitration_id),
                    "data": bytes(msg.data).hex().upper(),
                    "is_extended": bool(msg.is_extended_id),
                    "is_fd": bool(getattr(msg, "is_fd", False)),
                    "dlc": int(msg.dlc) if msg.dlc is not None else len(msg.data),
                }
            )

from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Optional

from app.config import get_settings
from app.gpu.runpod_client import RunpodClient


class GPUService:
    """
    Controls RunPod GPU pod lifecycle with an optional idle auto-stop timer.
    Keeps state in-memory (sufficient for single-instance CPU server).
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = RunpodClient()
        self._stop_timer: Optional[threading.Timer] = None
        self._active_until: Optional[datetime] = None

    def start(self) -> dict:
        data = self.client.start_pod()
        self._schedule_stop()
        return data

    def stop(self) -> dict:
        self._cancel_timer()
        data = self.client.stop_pod()
        self._active_until = None
        return data

    def status(self) -> dict:
        return self.client.get_status()

    def _schedule_stop(self):
        self._cancel_timer()
        minutes = max(1, self.settings.runpod_idle_timeout_minutes)
        self._active_until = datetime.utcnow() + timedelta(minutes=minutes)
        self._stop_timer = threading.Timer(minutes * 60, self._auto_stop)
        self._stop_timer.daemon = True
        self._stop_timer.start()

    def _cancel_timer(self):
        if self._stop_timer:
            self._stop_timer.cancel()
            self._stop_timer = None

    def _auto_stop(self):
        try:
            self.client.stop_pod()
        finally:
            self._active_until = None
            self._stop_timer = None


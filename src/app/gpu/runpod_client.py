from __future__ import annotations

import httpx
from typing import Any, Dict, Optional

from app.config import get_settings


class RunpodClient:
    """
    Minimal client for RunPod pod lifecycle (start/stop/status).
    Uses Option A: control an existing pod by ID.
    """

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.runpod_api_key or not self.settings.runpod_pod_id:
            raise ValueError("RunPod API key and pod ID are required for GPU control.")
        self.client = httpx.Client(timeout=30)

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.runpod_api_key}",
            "Content-Type": "application/json",
        }

    def _url(self, suffix: str) -> str:
        return f"{self.settings.runpod_api_base}/{suffix}"

    def start_pod(self) -> Dict[str, Any]:
        resp = self.client.post(
            self._url(f"{self.settings.runpod_pod_id}/start"), headers=self.headers
        )
        resp.raise_for_status()
        return resp.json()

    def stop_pod(self) -> Dict[str, Any]:
        resp = self.client.post(
            self._url(f"{self.settings.runpod_pod_id}/stop"), headers=self.headers
        )
        resp.raise_for_status()
        return resp.json()

    def get_status(self) -> Dict[str, Any]:
        resp = self.client.get(
            self._url(f"{self.settings.runpod_pod_id}"), headers=self.headers
        )
        resp.raise_for_status()
        return resp.json()


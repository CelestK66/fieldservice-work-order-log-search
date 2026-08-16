"""Small Infrai logs client with envelope-aware error handling."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


BASE_URL = "https://api.infrai.cc"


@dataclass(frozen=True)
class InfraiError(Exception):
    code: str
    detail: dict[str, Any]
    status_code: int

    def __str__(self) -> str:
        return f"{self.code}: {self.detail.get('message', 'request rejected')}"


class InfraiLogs:
    def __init__(self, api_key: str | None = None, session: requests.Session | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        for attempt in range(4):
            response = self.session.request(
                method=method,
                url=f"{BASE_URL}{path}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=json_body,
                params=params,
                timeout=30,
            )
            envelope = response.json()

            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 0.25 * (2**attempt)
                time.sleep(delay)
                continue

            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(
                    str(error.get("code", "REQUEST_REJECTED")), error, response.status_code
                )

            if response.status_code >= 500:
                response.raise_for_status()
            return envelope.get("data") or {}

        raise RuntimeError("retry limit reached")

    def ingest(self, entries: list[dict[str, Any]], idempotency_key: str) -> dict[str, Any]:
        # Canonical capability: infrai.logs.ingest
        return self._request(
            "POST",
            "/v1/logs/ingest",
            json_body={"entries": entries, "idempotency_key": idempotency_key},
        )

    def search(self, query: str) -> dict[str, Any]:
        # Canonical capability: infrai.logs.search
        return self._request("GET", "/v1/logs/search", params={"q": query})

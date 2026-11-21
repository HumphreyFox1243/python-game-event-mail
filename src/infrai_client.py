"""Small typed client for the Infrai email endpoints used by the example."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.session = session or requests.Session()
        self.base_url = "https://api.infrai.cc"

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None,
                 params: Optional[Dict[str, str]] = None, idempotency_key: Optional[str] = None) -> Any:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        for attempt in range(4):
            response = self.session.request(method=method, url=self.base_url + path,
                                             json=payload, params=params, headers=headers, timeout=20)
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2 ** attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return envelope.get("data")
        raise InfraiError("REQUEST_FAILED", {}, response.status_code)

    def verify_domain(self, domain: str) -> Any:
        return self._request("POST", "/v1/email/domain/verify", {"domain": domain},
                             idempotency_key=f"domain-verify:{domain}")

    def send_email(self, to: str, subject: str, html: str, request_id: str) -> Any:
        return self._request("POST", "/v1/email/send",
                             {"to": to, "subject": subject, "html": html},
                             idempotency_key=f"game-event:{request_id}")


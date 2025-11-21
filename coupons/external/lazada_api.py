from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict, Optional

import requests
from django.conf import settings


class LazadaAPI:
    BASE_URL = "https://api.lazada.vn/rest"

    def __init__(self, app_key: Optional[str] = None, app_secret: Optional[str] = None, access_token: Optional[str] = None) -> None:
        self.app_key = app_key or settings.LAZADA_APP_KEY
        self.app_secret = app_secret or settings.LAZADA_APP_SECRET
        self.access_token = access_token or settings.LAZADA_ACCESS_TOKEN

    def _build_signature(self, path: str, params: Dict[str, Any]) -> str:
        sorted_params = "".join(f"{k}{params[k]}" for k in sorted(params.keys()))
        to_sign = f"{path}{sorted_params}"
        digest = hmac.new(self.app_secret.encode("utf-8"), to_sign.encode("utf-8"), hashlib.sha256).hexdigest().upper()
        return digest

    def _base_payload(self) -> Dict[str, Any]:
        return {
            "app_key": self.app_key,
            "timestamp": str(int(time.time() * 1000)),
            "sign_method": "sha256",
        }

    def _get(self, endpoint: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = self._base_payload()
        if extra:
            payload.update(extra)

        if self.access_token:
            payload["access_token"] = self.access_token

        payload["sign"] = self._build_signature(endpoint, payload)

        response = requests.get(f"{self.BASE_URL}{endpoint}", params=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def fetch_vouchers(self, status: Optional[str] = None, page_size: int = 20, page_no: int = 1) -> Dict[str, Any]:
        params = {
            "page_size": page_size,
            "page_no": page_no,
        }
        if status:
            params["status"] = status
        return self._get("/promotion/vouchers/get", params)


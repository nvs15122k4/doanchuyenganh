from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional

import requests
from django.conf import settings


class ShopeeAPI:
    BASE_URL = "https://partner.shopeemobile.com"

    def __init__(
        self,
        partner_id: Optional[int] = None,
        partner_key: Optional[str] = None,
        shop_id: Optional[int] = None,
        access_token: Optional[str] = None,
    ) -> None:
        self.partner_id = partner_id or settings.SHOPEE_PARTNER_ID
        self.partner_key = partner_key or settings.SHOPEE_PARTNER_KEY
        self.shop_id = shop_id or settings.SHOPEE_SHOP_ID
        self.access_token = access_token or settings.SHOPEE_ACCESS_TOKEN

    def _sign(self, path: str, timestamp: int, body: str = "") -> str:
        base_string = f"{self.partner_id}{path}{timestamp}{self.access_token}{self.shop_id}{body}"
        return hmac.new(self.partner_key.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def _request(self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        timestamp = int(time.time())
        path = f"/api/v2{endpoint}"

        body = json.dumps(payload or {})
        signature = self._sign(path, timestamp, body if method == "POST" else "")

        headers = {"Content-Type": "application/json"}
        params = {
            "partner_id": self.partner_id,
            "timestamp": timestamp,
            "sign": signature,
            "shop_id": self.shop_id,
            "access_token": self.access_token,
        }

        url = f"{self.BASE_URL}{path}"
        response = requests.request(method, url, headers=headers, params=params, data=body if method == "POST" else None, timeout=30)
        response.raise_for_status()
        return response.json()

    def fetch_vouchers(self, page_no: int = 1, page_size: int = 20, status: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "page_no": page_no,
            "page_size": page_size,
        }
        if status:
            payload["voucher_status"] = status
        return self._request("GET", "/voucher/get_voucher_list", payload)


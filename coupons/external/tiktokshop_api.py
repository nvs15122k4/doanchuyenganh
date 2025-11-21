from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional

import requests
from django.conf import settings


class TiktokShopAPI:
    BASE_URL = "https://open-api.tiktokglobalshop.com"

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        shop_cipher: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> None:
        self.app_key = app_key or settings.TIKTOK_APP_KEY
        self.app_secret = app_secret or settings.TIKTOK_APP_SECRET
        self.shop_cipher = shop_cipher or settings.TIKTOK_SHOP_CIPHER
        self.access_token = access_token or settings.TIKTOK_ACCESS_TOKEN

    def _sign(self, path: str, params: Dict[str, Any]) -> str:
        sorted_items = "".join(f"{k}{params[k]}" for k in sorted(params))
        base_str = f"{self.app_secret}{path}{sorted_items}{self.app_secret}"
        return hmac.new(self.app_secret.encode("utf-8"), base_str.encode("utf-8"), hashlib.sha256).hexdigest().lower()

    def _request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = int(time.time())
        base_params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "shop_cipher": self.shop_cipher,
            "access_token": self.access_token,
            "version": payload.get("version", "202309"),
        }

        params = {**base_params, **payload}
        sign = self._sign(endpoint, params)
        params["sign"] = sign

        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(params), timeout=30)
        response.raise_for_status()
        return response.json()

    def fetch_promotions(self, page_number: int = 1, page_size: int = 20, status: Optional[int] = None) -> Dict[str, Any]:
        payload = {
            "page_number": page_number,
            "page_size": page_size,
        }
        if status:
            payload["promotion_status"] = status
        return self._request("/promotion/202309/promotions/search", payload)


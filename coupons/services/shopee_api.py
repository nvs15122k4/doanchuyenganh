import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings


class ShopeeAPIClient:
    BASE_URL = "https://partner.shopeemobile.com"

    def __init__(
        self,
        partner_id: Optional[int] = None,
        partner_key: Optional[str] = None,
        shop_id: Optional[int] = None,
        access_token: Optional[str] = None,
    ):
        self.partner_id = partner_id or self._safe_int(settings.SHOPEE_PARTNER_ID)
        self.partner_key = partner_key or settings.SHOPEE_PARTNER_KEY
        self.shop_id = shop_id or self._safe_int(settings.SHOPEE_SHOP_ID)
        self.access_token = access_token or settings.SHOPEE_ACCESS_TOKEN
        self.session = requests.Session()

    @staticmethod
    def _safe_int(value: Optional[str]) -> Optional[int]:
        try:
            return int(value) if value else None
        except ValueError:
            return None

    def is_configured(self) -> bool:
        return all([self.partner_id, self.partner_key, self.shop_id, self.access_token])

    def _sign(self, path: str, timestamp: int, body: Dict[str, Any]) -> str:
        body_str = json.dumps(body, separators=(",", ":"))
        base_string = f"{self.partner_id}{path}{timestamp}{self.access_token}{self.shop_id}{body_str}"
        return hmac.new(
            self.partner_key.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def get_vouchers(self, page_size: int = 20, page_no: int = 1) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []

        path = "/api/v2/voucher/get_voucher_list"
        timestamp = int(time.time())
        body = {
            "page_no": page_no,
            "page_size": min(page_size, 100),
            "voucher_status": "ongoing",
        }
        sign = self._sign(path, timestamp, body)
        url = f"{self.BASE_URL}{path}"
        params = {
            "partner_id": self.partner_id,
            "timestamp": timestamp,
            "access_token": self.access_token,
            "shop_id": self.shop_id,
            "sign": sign,
        }
        try:
            response = self.session.get(url, params=params, json=body, timeout=20)
            response.raise_for_status()
            data = response.json()
            return data.get("response", {}).get("voucher_list", [])
        except requests.RequestException:
            return []


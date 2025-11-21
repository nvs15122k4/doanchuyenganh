import hashlib
import hmac
import time
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings


class TikTokShopAPIClient:
    BASE_URL = "https://open-api.tiktokglobalshop.com"

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        shop_cipher: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.app_key = app_key or settings.TIKTOK_APP_KEY
        self.app_secret = app_secret or settings.TIKTOK_APP_SECRET
        self.shop_cipher = shop_cipher or settings.TIKTOK_SHOP_CIPHER
        self.access_token = access_token or settings.TIKTOK_ACCESS_TOKEN
        self.session = requests.Session()

    def is_configured(self) -> bool:
        return all([self.app_key, self.app_secret, self.shop_cipher, self.access_token])

    def _sign(self, path: str, params: Dict[str, Any]) -> str:
        sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
        payload = f"{self.app_secret}{path}{sorted_params}{self.app_secret}"
        return hmac.new(
            self.app_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def get_seller_vouchers(self, page_number: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []

        path = "/promotion/202309/seller_vouchers/search"
        timestamp = int(time.time())
        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "shop_cipher": self.shop_cipher,
            "version": "202309",
            "page_number": page_number,
            "page_size": min(page_size, 50),
            "voucher_status": 1,
            "access_token": self.access_token,
        }
        params["sign"] = self._sign(path, params)
        try:
            response = self.session.post(
                f"{self.BASE_URL}{path}",
                data=params,
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("vouchers", [])
        except requests.RequestException:
            return []


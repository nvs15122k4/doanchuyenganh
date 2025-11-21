import hashlib
import hmac
import time
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings


class LazadaAPIClient:
    BASE_URL = "https://api.lazada.com/rest"

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.app_key = app_key or settings.LAZADA_APP_KEY
        self.app_secret = app_secret or settings.LAZADA_APP_SECRET
        self.access_token = access_token or settings.LAZADA_ACCESS_TOKEN
        self.session = requests.Session()

    def is_configured(self) -> bool:
        return all([self.app_key, self.app_secret, self.access_token])

    def _sign(self, path: str, params: Dict[str, Any]) -> str:
        sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
        payload = f"{path}{sorted_params}"
        return hmac.new(
            self.app_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()

    def _build_params(self, base_params: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = str(int(time.time() * 1000))
        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "sign_method": "sha256",
            **base_params,
        }
        params["sign"] = self._sign("/promotion/vouchers/get", params)
        return params

    def get_vouchers(self, page_size: int = 10) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []

        path = "/promotion/vouchers/get"
        params = {
            "access_token": self.access_token,
            "page_size": min(page_size, 100),
            "page_no": 1,
            "status": "1",
        }
        signed_params = self._build_params(params)
        try:
            response = self.session.get(
                f"{self.BASE_URL}{path}",
                params=signed_params,
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("result", {})
            return result.get("vouchers", []) if isinstance(result, dict) else []
        except requests.RequestException:
            return []


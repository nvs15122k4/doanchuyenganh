import logging
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """Lightweight wrapper for Supabase REST API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        anon_key: Optional[str] = None,
        service_role_key: Optional[str] = None,
        table_name: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.SUPABASE_URL).rstrip("/")
        self.table_name = table_name or settings.SUPABASE_COUPONS_TABLE
        self.anon_key = anon_key or settings.SUPABASE_ANON_KEY
        self.service_role_key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY
        self.session = requests.Session()

    @property
    def _rest_base(self) -> str:
        return f"{self.base_url}/rest/v1"

    def _headers(self, use_service_role: bool = False) -> Dict[str, str]:
        token = self.service_role_key if use_service_role else self.anon_key
        return {
            "apikey": token,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def fetch_coupons(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch coupons stored in Supabase table."""
        if not self.table_name:
            logger.warning("Supabase table name is not configured.")
            return []

        params = {
            "select": "*",
            "order": "created_at.desc",
            "limit": limit,
        }

        try:
            response = self.session.get(
                f"{self._rest_base}/{self.table_name}",
                headers=self._headers(),
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
            return []
        except requests.RequestException as exc:
            logger.error("Failed to fetch coupons from Supabase: %s", exc, exc_info=True)
            return []

    def upsert_coupon(self, payload: Dict[str, Any]) -> bool:
        """Insert or update a coupon row in Supabase."""
        if not payload:
            return False

        try:
            response = self.session.post(
                f"{self._rest_base}/{self.table_name}",
                headers={
                    **self._headers(use_service_role=True),
                    "Prefer": "resolution=merge-duplicates",
                },
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.error("Failed to upsert coupon to Supabase: %s", exc, exc_info=True)
            return False

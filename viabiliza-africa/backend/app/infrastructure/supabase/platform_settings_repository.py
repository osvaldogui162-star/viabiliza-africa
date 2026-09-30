from datetime import datetime, timezone

from supabase import Client

from app.domain.repositories.platform_settings_repository import IPlatformSettingsRepository
from app.infrastructure.supabase.response_helpers import get_single_row

PROMOTION_KEY = "pricing_promotion"


class SupabasePlatformSettingsRepository(IPlatformSettingsRepository):
    TABLE = "platform_settings"

    def __init__(self, client: Client) -> None:
        self._client = client

    def get_pricing_promotion(self) -> dict:
        try:
            response = (
                self._client.table(self.TABLE)
                .select("settings")
                .eq("setting_key", PROMOTION_KEY)
                .limit(1)
                .execute()
            )
            row = get_single_row(response)
            if row and isinstance(row.get("settings"), dict):
                return row["settings"]
        except Exception:
            pass
        return {"active": False}

    def set_pricing_promotion(self, settings: dict) -> dict:
        payload = {
            "setting_key": PROMOTION_KEY,
            "settings": settings,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._client.table(self.TABLE).upsert(payload, on_conflict="setting_key").execute()
        return settings

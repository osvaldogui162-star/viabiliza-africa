from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from supabase import Client

from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.payment_repository import ISubscriptionPaymentRepository
from app.infrastructure.supabase.response_helpers import get_single_row


def _map_payment(row: dict) -> dict:
    return {
        "id": str(row["id"]),
        "user_id": str(row["user_id"]),
        "plan_code": row["plan_code"],
        "billing_cycle": row["billing_cycle"],
        "amount": str(row["amount"]),
        "currency": row["currency"],
        "payment_method": row["payment_method"],
        "status": row["status"],
        "merchant_transaction_id": row["merchant_transaction_id"],
        "appypay_charge_id": row.get("appypay_charge_id"),
        "appypay_status": row.get("appypay_status"),
        "phone_number": row.get("phone_number"),
        "reference_entity": row.get("reference_entity"),
        "reference_number": row.get("reference_number"),
        "description": row.get("description"),
        "raw_response": row.get("raw_response") or {},
        "error_message": row.get("error_message"),
        "paid_at": row["paid_at"] if row.get("paid_at") else None,
        "subscription_id": row.get("subscription_id"),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


class SupabaseSubscriptionPaymentRepository(ISubscriptionPaymentRepository):
    TABLE = "subscription_payments"

    def __init__(self, client: Client) -> None:
        self._client = client

    def create(
        self,
        *,
        user_id: UUID,
        plan_code: str,
        billing_cycle: str,
        amount: Decimal,
        currency: str,
        payment_method: str,
        merchant_transaction_id: str,
        description: str,
        phone_number: str | None = None,
    ) -> dict:
        payload = {
            "user_id": str(user_id),
            "plan_code": plan_code,
            "billing_cycle": billing_cycle,
            "amount": str(amount),
            "currency": currency,
            "payment_method": payment_method,
            "status": "pending",
            "merchant_transaction_id": merchant_transaction_id,
            "description": description,
            "phone_number": phone_number,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if not row:
            raise RuntimeError("Falha ao criar pagamento")
        return _map_payment(row)

    def find_by_id(self, payment_id: UUID, *, user_id: UUID | None = None) -> dict | None:
        query = self._client.table(self.TABLE).select("*").eq("id", str(payment_id))
        if user_id:
            query = query.eq("user_id", str(user_id))
        response = query.limit(1).execute()
        row = get_single_row(response)
        return _map_payment(row) if row else None

    def find_all(
        self,
        *,
        status: str | None = None,
        user_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        query = self._client.table(self.TABLE).select("*", count="exact")
        if status:
            query = query.eq("status", status)
        if user_id:
            query = query.eq("user_id", str(user_id))
        response = (
            query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        )
        rows = response.data or []
        total = response.count if response.count is not None else len(rows)
        return [_map_payment(row) for row in rows], total

    def get_admin_stats(self) -> dict:
        response = self._client.table(self.TABLE).select("status, amount, currency, paid_at").execute()
        rows = response.data or []
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        paid_total = Decimal("0")
        paid_count = pending_count = failed_count = 0
        paid_month_count = 0
        paid_month_amount = Decimal("0")
        primary_currency = "AOA"

        for row in rows:
            status = row.get("status", "")
            amount = Decimal(str(row.get("amount") or 0))
            if row.get("currency"):
                primary_currency = row["currency"]

            if status == "paid":
                paid_count += 1
                paid_total += amount
                paid_at_raw = row.get("paid_at")
                if paid_at_raw:
                    paid_at = datetime.fromisoformat(str(paid_at_raw).replace("Z", "+00:00"))
                    if paid_at >= month_start:
                        paid_month_count += 1
                        paid_month_amount += amount
            elif status == "pending":
                pending_count += 1
            elif status in ("failed", "cancelled", "expired"):
                failed_count += 1

        return {
            "paid_total_amount": str(paid_total),
            "paid_currency": primary_currency,
            "paid_count": paid_count,
            "pending_count": pending_count,
            "failed_count": failed_count,
            "paid_this_month_count": paid_month_count,
            "paid_this_month_amount": str(paid_month_amount),
        }

    def find_latest_for_user(self, user_id: UUID) -> dict | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_payment(row) if row else None

    def find_by_merchant_transaction_id(self, merchant_transaction_id: str) -> dict | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("merchant_transaction_id", merchant_transaction_id)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_payment(row) if row else None

    def update_from_appypay(
        self,
        payment_id: UUID,
        *,
        appypay_charge_id: str | None = None,
        appypay_status: str | None = None,
        status: str | None = None,
        reference_entity: str | None = None,
        reference_number: str | None = None,
        raw_response: dict | None = None,
        error_message: str | None = None,
        paid_at: datetime | None = None,
        subscription_id: UUID | None = None,
    ) -> dict:
        payload: dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if appypay_charge_id is not None:
            payload["appypay_charge_id"] = appypay_charge_id
        if appypay_status is not None:
            payload["appypay_status"] = appypay_status
        if status is not None:
            payload["status"] = status
        if reference_entity is not None:
            payload["reference_entity"] = reference_entity
        if reference_number is not None:
            payload["reference_number"] = reference_number
        if raw_response is not None:
            payload["raw_response"] = raw_response
        if error_message is not None:
            payload["error_message"] = error_message
        if paid_at is not None:
            payload["paid_at"] = paid_at.isoformat()
        if subscription_id is not None:
            payload["subscription_id"] = str(subscription_id)

        response = (
            self._client.table(self.TABLE).update(payload).eq("id", str(payment_id)).execute()
        )
        row = get_single_row(response)
        if not row:
            raise EntityNotFoundError("Pagamento", str(payment_id))
        return _map_payment(row)

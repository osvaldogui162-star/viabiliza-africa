from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from uuid import UUID


class ISubscriptionPaymentRepository(ABC):
    @abstractmethod
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
        ...

    @abstractmethod
    def find_by_id(self, payment_id: UUID, *, user_id: UUID | None = None) -> dict | None:
        ...

    @abstractmethod
    def find_by_merchant_transaction_id(self, merchant_transaction_id: str) -> dict | None:
        ...

    @abstractmethod
    def find_all(
        self,
        *,
        status: str | None = None,
        user_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        ...

    @abstractmethod
    def get_admin_stats(self) -> dict:
        ...

    @abstractmethod
    def find_latest_for_user(self, user_id: UUID) -> dict | None:
        ...

    @abstractmethod
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
        ...

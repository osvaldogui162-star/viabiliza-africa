from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class IAccountErpBillingRepository(ABC):
    @abstractmethod
    def get_connection(self, user_id: UUID) -> dict | None:
        ...

    @abstractmethod
    def upsert_connection(
        self,
        user_id: UUID,
        *,
        provider_code: str,
        config: dict,
        auto_fiscal_on_payment: bool,
        connection_status: str,
        last_error: str | None = None,
    ) -> dict:
        ...

    @abstractmethod
    def update_connection_status(
        self,
        user_id: UUID,
        *,
        connection_status: str,
        last_test_at: datetime | None = None,
        last_error: str | None = None,
    ) -> dict | None:
        ...

    @abstractmethod
    def create_fiscal_document(
        self,
        *,
        user_id: UUID,
        payment_id: UUID | None,
        provider_code: str,
        status: str,
        external_ref: str | None = None,
        document_payload: dict | None = None,
        agt_export_xml: str | None = None,
        error_message: str | None = None,
        issued_at: datetime | None = None,
    ) -> dict:
        ...

    @abstractmethod
    def find_fiscal_by_payment(self, payment_id: UUID) -> dict | None:
        ...

    @abstractmethod
    def list_fiscal_documents(self, user_id: UUID, *, limit: int = 20) -> list[dict]:
        ...

    @abstractmethod
    def get_fiscal_document(self, user_id: UUID, document_id: UUID) -> dict | None:
        ...

    @abstractmethod
    def user_has_paid_subscription_payment(self, user_id: UUID) -> bool:
        ...

from decimal import Decimal
from uuid import UUID

from app.application.interfaces.hash_service import IHashService
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.data_source import DataSource


class CostItemHashBuilder:
    """Constrói payload canónico e hash SHA-256 para itens OPEX/CAPEX."""

    def __init__(self, hash_service: IHashService) -> None:
        self._hash = hash_service

    def build_hash(
        self,
        *,
        project_id: UUID,
        item_type: CostItemType,
        category: str,
        description: str,
        quantity: Decimal,
        unit: str,
        unit_price: Decimal,
        source: DataSource,
        supplier_name: str | None = None,
    ) -> str:
        payload = {
            "project_id": str(project_id),
            "item_type": item_type.value,
            "category": category.strip(),
            "description": description.strip(),
            "quantity": format(quantity, "f"),
            "unit": unit.strip(),
            "unit_price": format(unit_price, "f"),
            "source": source.value,
            "supplier_name": (supplier_name or "").strip(),
        }
        return self._hash.hash_dict(payload)

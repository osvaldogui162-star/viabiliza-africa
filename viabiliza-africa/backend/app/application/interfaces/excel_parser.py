from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ExcelCostItemRow:
    item_type: str
    category: str
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    supplier_name: str | None
    supplier_nif: str | None = None


class IExcelParser(ABC):
    """Contrato para parsing de ficheiros Excel OPEX/CAPEX."""

    MAX_ROWS: int = 1000

    @abstractmethod
    def parse_cost_items(self, file_bytes: bytes) -> list[ExcelCostItemRow]:
        ...

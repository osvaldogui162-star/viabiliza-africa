from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class QRCodeResult:
    data: str
    image_base64: str


class IQRCodeService(ABC):
    """Contrato para geração de QR Codes de verificação."""

    @abstractmethod
    def generate(self, verification_url: str) -> QRCodeResult:
        ...

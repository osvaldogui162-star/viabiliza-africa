import base64
import io

import qrcode
from qrcode.constants import ERROR_CORRECT_H

from app.application.interfaces.qr_code_service import IQRCodeService, QRCodeResult


class QRCodeService(IQRCodeService):
    """Geração de QR Codes para orçamentos rastreáveis."""

    def generate(self, verification_url: str) -> QRCodeResult:
        # URL longa (hash SHA-256) → QR denso; módulos grandes + margem para scan móvel
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_H,
            box_size=12,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        return QRCodeResult(data=verification_url, image_base64=image_base64)

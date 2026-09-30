"""Extrair dados de empresa a partir de documento carregado."""

from __future__ import annotations

from app.application.services.company_document_extractor import CompanyDocumentExtractor
from app.domain.exceptions.domain_exceptions import ValidationError


class ExtractCompanyDocumentUseCase:
    def __init__(self, extractor: CompanyDocumentExtractor) -> None:
        self._extractor = extractor

    def execute(self, *, file_bytes: bytes, filename: str) -> dict:
        if not file_bytes:
            raise ValidationError("Ficheiro vazio")
        if len(file_bytes) > 10 * 1024 * 1024:
            raise ValidationError("Ficheiro demasiado grande (máx. 10 MB)")

        try:
            result = self._extractor.extract(file_bytes, filename=filename)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        return {"extracted": result, "filename": filename}

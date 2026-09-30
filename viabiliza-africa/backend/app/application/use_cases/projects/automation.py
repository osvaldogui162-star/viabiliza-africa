from app.domain.enums.financing_bank import FinancingBank
from app.domain.exceptions.domain_exceptions import ValidationError
from app.infrastructure.external.angola_api_client import AngolaApiClient
from app.infrastructure.scraping.agt_nif_lookup import AgtNifLookupService
from app.infrastructure.scraping.angolan_bank_rate_scraper import AngolanBankRateScraper


class LookupCompanyByNifUseCase:
    def __init__(self, nif_service: AgtNifLookupService) -> None:
        self._nif = nif_service

    def execute(self, nif: str) -> dict:
        try:
            result = self._nif.lookup(nif)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        except LookupError as exc:
            raise ValidationError(str(exc)) from exc
        except Exception as exc:
            raise ValidationError(
                f"Falha ao consultar NIF na AGT: {exc}. "
                "Tente novamente ou consulte https://portaldocontribuinte.minfin.gov.ao/consultar-nif-do-contribuinte"
            ) from exc

        if not result.company_name:
            raise ValidationError(
                "NIF sem dados de empresa no portal AGT. Confirme o número."
            )

        return {
            "nif": result.nif,
            "company_name": result.company_name,
            "address": result.address,
            "activity": result.activity,
            "status": result.status,
            "source_url": result.source_url,
            "fields": result.raw_fields,
        }


class ListFinancingBanksUseCase:
    def __init__(self, rate_scraper: AngolanBankRateScraper) -> None:
        self._rates = rate_scraper

    def execute(self) -> dict:
        return {"items": self._rates.list_banks(), "total": len(FinancingBank.values())}


class GetBankDiscountRateUseCase:
    def __init__(self, rate_scraper: AngolanBankRateScraper) -> None:
        self._rates = rate_scraper

    def execute(self, bank_code: str, *, sector: str | None = None) -> dict:
        try:
            quote = self._rates.get_discount_rate(bank_code, sector=sector)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        except LookupError as exc:
            raise ValidationError(str(exc)) from exc
        except Exception as exc:
            raise ValidationError(
                f"Falha ao obter taxa do banco: {exc}"
            ) from exc

        return {
            "bank_code": quote.bank_code,
            "bank_name": quote.bank_name,
            "discount_rate": format(quote.rate_percent, "f"),
            "product_label": quote.product_label,
            "source_url": quote.source_url,
            "currency": quote.currency,
        }


class ValidateAngolaBiUseCase:
    def __init__(self, angola_api: AngolaApiClient) -> None:
        self._angola = angola_api

    def execute(self, bi: str) -> dict:
        try:
            result = self._angola.validate_bi(bi)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        except Exception as exc:
            raise ValidationError(f"Falha ao validar BI: {exc}") from exc

        if not result.valid:
            raise ValidationError(result.message)

        return {
            "valid": True,
            "message": result.message,
            "source": result.source,
            "normalized_value": result.normalized_value,
        }


class ValidateAngolaPhoneUseCase:
    def __init__(self, angola_api: AngolaApiClient) -> None:
        self._angola = angola_api

    def execute(self, phone: str, *, optional: bool = False) -> dict:
        try:
            result = self._angola.validate_phone(phone, optional=optional)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        except Exception as exc:
            raise ValidationError(f"Falha ao validar telefone: {exc}") from exc

        if not result.valid:
            raise ValidationError(result.message)

        return {
            "valid": True,
            "message": result.message,
            "source": result.source,
            "operator": result.operator,
            "normalized_value": result.normalized_value,
        }


class ListBankBranchesUseCase:
    def execute(self, bank_code: str, *, province: str | None = None) -> dict:
        from app.domain.catalog.angolan_bank_branches import list_bank_branches
        from app.domain.enums.financing_bank import FinancingBank

        if not FinancingBank.is_valid(bank_code):
            raise ValidationError(
                f"Banco inválido. Valores: {', '.join(FinancingBank.values())}"
            )
        branches = list_bank_branches(bank_code, province=province)
        return {"bank_code": bank_code, "items": branches, "total": len(branches)}

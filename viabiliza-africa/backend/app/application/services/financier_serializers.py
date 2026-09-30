from app.domain.enums.financing_bank import FinancingBank
from app.domain.entities.project_financing import ProjectFinancing


def bank_meta(bank_code: str) -> dict:
    code = bank_code.lower()
    try:
        fb = FinancingBank(code)
        return {
            "code": code,
            "label_pt": fb.label_pt,
            "label_en": fb.label_pt,
            "logo_path": fb.logo_path,
            "website": fb.website,
        }
    except ValueError:
        return {"code": code, "label_pt": code.upper(), "label_en": code.upper(), "logo_path": None}


def financing_output(
    f: ProjectFinancing, *, project_name: str, company_name: str | None, sector: str
) -> dict:
    return {
        "id": str(f.id),
        "project_id": str(f.project_id),
        "project_name": project_name,
        "company_name": company_name,
        "sector": sector,
        "bank": bank_meta(f.bank_code),
        "decision": f.decision,
        "workflow_status": f.workflow_status,
        "approved_amount": str(f.approved_amount),
        "currency": f.currency,
        "disbursed_amount": str(f.disbursed_amount),
        "monitoring_status": f.monitoring_status,
        "decision_at": f.decision_at.isoformat(),
        "submitted_at": f.created_at.isoformat(),
        "bank_decided_at": f.bank_decided_at.isoformat() if f.bank_decided_at else None,
        "term_months": f.term_months,
        "interest_rate_pct": str(f.interest_rate_pct) if f.interest_rate_pct is not None else None,
        "notes": f.notes,
    }

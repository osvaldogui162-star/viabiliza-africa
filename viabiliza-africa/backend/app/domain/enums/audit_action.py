from enum import Enum


class AuditAction(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    IMPORTED = "imported"
    SCRAPING_COMPLETED = "scraping_completed"
    SUPPLIER_SELECTED = "supplier_selected"
    BUDGET_GENERATED = "budget_generated"
    BUDGET_APPROVED = "budget_approved"
    PROFORMA_GENERATED = "proforma_generated"
    REPORT_GENERATED = "report_generated"
    REPORT_SENT_EMAIL = "report_sent_email"
    REPORT_SHARED = "report_shared"
    REPORT_SUBMITTED_BANK = "report_submitted_bank"
    REPORT_PRINTED = "report_printed"
    CONFIG_UPDATED = "config_updated"
    PLAN_UPDATED = "plan_updated"
    SUBSCRIPTION_ASSIGNED = "subscription_assigned"

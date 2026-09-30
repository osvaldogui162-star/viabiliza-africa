from enum import Enum


class AuditEntityType(str, Enum):
    COST_ITEM = "cost_item"
    BUDGET = "budget"
    PROFORMA = "proforma"
    SCRAPING_JOB = "scraping_job"
    SCRAPING_RESULT = "scraping_result"
    REPORT = "report"
    SYSTEM_CONFIG = "system_config"
    SUBSCRIPTION_PLAN = "subscription_plan"
    USER_SUBSCRIPTION = "user_subscription"

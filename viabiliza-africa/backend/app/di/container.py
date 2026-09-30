from dataclasses import dataclass

from app.application.services.analysis_access_policy import AnalysisAccessPolicy
from app.application.services.analysis_context_builder import AnalysisContextBuilder
from app.application.services.collaboration_access_policy import CollaborationAccessPolicy
from app.application.services.kanban_board_service import KanbanBoardService
from app.application.services.kanban_task_service import KanbanTaskService
from app.application.services.task_dependency_validator import TaskDependencyValidator
from app.application.services.cost_item_hash_builder import CostItemHashBuilder
from app.application.services.ingestion_access_policy import IngestionAccessPolicy
from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.shared_project_capability_policy import SharedProjectCapabilityPolicy
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.report_access_policy import ReportAccessPolicy
from app.application.services.report_data_aggregator import ReportDataAggregator
from app.application.services.sector_profile_service import SectorProfileService
from app.application.services.strategic_insights_service import StrategicInsightsService
from app.application.services.company_document_extractor import CompanyDocumentExtractor
from app.application.use_cases.analysis.benchmarks import CompareBenchmarksUseCase
from app.application.use_cases.analysis.calculate_indicators import CalculateIndicatorsUseCase
from app.application.use_cases.analysis.export_indicators import ExportIndicatorsUseCase
from app.application.use_cases.analysis.list_analyses import GetAnalysisUseCase, ListAnalysesUseCase
from app.application.use_cases.analysis.monte_carlo import ListMonteCarloUseCase, RunMonteCarloUseCase
from app.application.use_cases.analysis.run_scenario_analysis import RunScenarioAnalysisUseCase
from app.application.use_cases.analysis.sensitivity import ListSensitivityUseCase, RunSensitivityUseCase
from app.application.use_cases.collaboration.chat import ListChatMessagesUseCase, SendChatMessageUseCase
from app.application.use_cases.collaboration.chat_realtime import (
    ChatPresenceUseCase,
    MarkChatReadUseCase,
    PollChatUseCase,
)
from app.application.use_cases.collaboration.kanban_integration import (
    GetKanbanIntegrationUseCase,
    SyncKanbanBoardUseCase,
)
from app.application.use_cases.collaboration.dependencies import (
    CreateTaskDependencyUseCase,
    DeleteTaskDependencyUseCase,
    ListTaskDependenciesUseCase,
)
from app.application.use_cases.collaboration.tasks import (
    CreateTaskUseCase,
    DeleteTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
    MoveTaskUseCase,
    UpdateTaskUseCase,
)
from app.application.use_cases.admin.audit_trail_global import GetGlobalAuditTrailUseCase
from app.application.use_cases.admin.budget_templates import (
    CreateBudgetTemplateUseCase,
    DeleteBudgetTemplateUseCase,
    ListBudgetTemplatesUseCase,
    SetDefaultBudgetTemplateUseCase,
    UpdateBudgetTemplateUseCase,
)
from app.application.use_cases.admin.get_access_logs import GetAccessLogsUseCase
from app.application.use_cases.admin.integrations import (
    GetIntegrationUseCase,
    ListIntegrationsUseCase,
    TestIntegrationUseCase,
    UpdateIntegrationUseCase,
)
from app.application.use_cases.admin.manage_users import (
    ApproveUserUseCase,
    ExtendUserAccessUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserRoleUseCase,
    UpdateUserUseCase,
)
from app.application.use_cases.admin.scraping_sources import (
    CreateScrapingSourceUseCase,
    DeleteScrapingSourceUseCase,
    ListScrapingSourcesAdminUseCase,
    UpdateScrapingSourceUseCase,
)
from app.application.use_cases.admin.admin_customers import ListAdminCustomersUseCase
from app.application.use_cases.admin.billing_overview import (
    GetBillingOverviewUseCase,
    ListAdminPaymentsUseCase,
)
from app.application.use_cases.admin.manage_pricing_promotion import ManagePricingPromotionUseCase
from app.application.use_cases.admin.sync_plans import SyncSubscriptionPlansUseCase
from app.application.use_cases.admin.subscriptions import (
    AssignUserSubscriptionUseCase,
    CreateSubscriptionPlanUseCase,
    DeleteSubscriptionPlanUseCase,
    ListSubscriptionPlansUseCase,
    ListUserSubscriptionsUseCase,
    UpdateSubscriptionPlanUseCase,
    UpdateUserSubscriptionStatusUseCase,
)
from app.application.use_cases.subscriptions.appy_pay_payments import (
    InitiateAppyPayPaymentUseCase,
    MockAppyPayReferenceUseCase,
    PollAppyPayPaymentUseCase,
)
from app.application.services.financier_portfolio_loader import FinancierPortfolioLoader
from app.application.use_cases.financier.financier_use_cases import (
    CreateProjectFinancingUseCase,
    DecideProjectFinancingUseCase,
    GetFinancierMonitoringUseCase,
    ListFinancierPendingApprovalsUseCase,
    ListFinancierPortfolioUseCase,
    ListProjectFinancingsUseCase,
)
from app.application.use_cases.financier.financier_portal_use_cases import (
    CreateFinancingDisbursementUseCase,
    CreateFinancingDocumentUseCase,
    ExportFinancierPortfolioReportUseCase,
    GetFinancierDashboardUseCase,
    GetFinancierProjectDetailUseCase,
    ListFinancierActivityUseCase,
    ListFinancierAlertsUseCase,
    ListFinancierDisbursementsUseCase,
    ListFinancierDocumentsUseCase,
    UpdateFinancingDisbursementUseCase,
    ValidateFinancingDocumentUseCase,
)
from app.application.use_cases.financier.billing_integration_use_cases import (
    ConfigureProjectBillingIntegrationUseCase,
    ExportFinancierCreditReportUseCase,
    GetProjectBillingIntegrationUseCase,
    ListFinancierBillingIntegrationsUseCase,
    RegenerateProjectBillingApiKeyUseCase,
    SyncBillingViaApiKeyUseCase,
    SyncProjectBillingIntegrationUseCase,
)
from app.application.use_cases.subscriptions.public_plans import (
    GetMySubscriptionUseCase,
    ListPublicPlansUseCase,
    PrepareCheckoutUseCase,
    SubscribeToPlanUseCase,
)
from app.application.use_cases.notifications.manage_notifications import (
    ListNotificationsUseCase,
    MarkAllNotificationsReadUseCase,
    MarkNotificationReadUseCase,
)
from app.application.services.notification_service import NotificationService
from app.application.services.registration_invite_fulfillment import (
    RegistrationInviteFulfillmentService,
)
from app.application.services.registration_policy_service import RegistrationPolicyService
from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.services.integration_config_service import IntegrationConfigService
from app.application.services.account_role_service import AccountRoleService
from app.application.services.commercial_pricing_service import CommercialPricingService
from app.application.services.financier_access_policy import FinancierAccessPolicy
from app.application.services.subscription_service import SubscriptionService
from app.application.services.user_access_enforcement import UserAccessEnforcementService
from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.auth.get_registration_status import GetRegistrationStatusUseCase
from app.application.use_cases.auth.google_auth import GoogleAuthUseCase
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.logout import LogoutUseCase
from app.application.use_cases.auth.recover_password import RecoverPasswordUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.application.use_cases.auth.reset_password import ResetPasswordUseCase
from app.application.use_cases.auth.update_user_preferences import UpdateUserPreferencesUseCase
from app.application.use_cases.auth.signup_otp import (
    RequestSignupOtpUseCase,
    ResendSignupOtpUseCase,
    VerifySignupOtpUseCase,
)
from app.application.use_cases.ingestion.audit_trail import GetAuditTrailUseCase
from app.application.use_cases.ingestion.auto_ingestion import (
    PreviewAutoIngestionUseCase,
    RunAutoIngestionUseCase,
)
from app.application.use_cases.ingestion.budgets import (
    ApproveBudgetUseCase,
    GenerateBudgetUseCase,
    GenerateProformaUseCase,
    GetBudgetUseCase,
    ListBudgetsUseCase,
    ListProformasUseCase,
    VerifyBudgetUseCase,
)
from app.application.use_cases.ingestion.cost_items import (
    CreateCostItemUseCase,
    DeleteCostItemUseCase,
    ImportCostItemsExcelUseCase,
    ListCostItemsUseCase,
    UpdateCostItemUseCase,
)
from app.application.use_cases.ingestion.scraping import (
    ExecuteScrapingUseCase,
    GetScrapingJobUseCase,
    ListScrapingSourcesUseCase,
    SelectSupplierUseCase,
)
from app.domain.catalog.sector_item_catalog import SectorItemCatalog
from app.application.use_cases.projects.create_project import CreateProjectUseCase
from app.application.use_cases.projects.delete_project import DeleteProjectUseCase
from app.application.use_cases.projects.generate_strategic_insights import GenerateStrategicInsightsUseCase
from app.application.use_cases.projects.extract_company_document import ExtractCompanyDocumentUseCase
from app.application.use_cases.projects.get_project import GetProjectUseCase
from app.application.use_cases.projects.get_sector_profile import GetSectorProfileUseCase
from app.application.use_cases.projects.list_projects import ListProjectsUseCase
from app.application.use_cases.projects.automation import (
    GetBankDiscountRateUseCase,
    ListBankBranchesUseCase,
    ListFinancingBanksUseCase,
    LookupCompanyByNifUseCase,
    ValidateAngolaBiUseCase,
    ValidateAngolaPhoneUseCase,
)
from app.application.use_cases.projects.share_project import (
    ListProjectSharesUseCase,
    RemoveProjectShareUseCase,
    ShareProjectUseCase,
)
from app.application.services.report_prerequisites_validator import ReportPrerequisitesValidator
from app.application.use_cases.projects.update_project import UpdateProjectUseCase
from app.application.use_cases.office.office_use_cases import (
    AdminListOfficesUseCase,
    ArchiveOfficeMemberUseCase,
    AssignOfficeMemberProjectsUseCase,
    CreateOfficeMemberUseCase,
    GetOfficeDashboardUseCase,
    ListOfficeMemberAccessUseCase,
    ListOfficeMembersUseCase,
    OfficeAccessPolicy,
    UpdateOfficeMemberUseCase,
)
from app.application.use_cases.reports.generate_report import GenerateReportUseCase
from app.application.use_cases.reports.report_actions import (
    DownloadReportUseCase,
    GetReportUseCase,
    GetSharedReportUseCase,
    ListReportsUseCase,
    PrintReportUseCase,
    SendReportEmailUseCase,
    ShareReportWhatsAppUseCase,
    SubmitReportToBankUseCase,
)
from app.application.use_cases.reports.verify_report import VerifyReportUseCase
from app.application.interfaces.email_service import IEmailService
from app.application.interfaces.hash_service import IHashService
from app.application.interfaces.password_hasher import IPasswordHasher
from app.application.interfaces.token_service import ITokenService
from app.config import Config
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.admin_config_repository import (
    IBudgetTemplateRepository,
    IIntegrationSettingsRepository,
    IScrapingSourceAdminRepository,
    ISubscriptionRepository,
)
from app.domain.repositories.analysis_repository import (
    IFinancialAnalysisRepository,
    IFinancialAssumptionsRepository,
    IMonteCarloRepository,
    ISectorBenchmarkRepository,
    ISensitivityRepository,
)
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.domain.repositories.budget_repository import IBudgetRepository
from app.domain.repositories.notification_repository import INotificationRepository
from app.domain.repositories.collaboration_repository import (
    IChatMessageRepository,
    IChatReadStateRepository,
    IKanbanTaskRepository,
    IProjectPresenceRepository,
    ITaskDependencyRepository,
)
from app.domain.repositories.kanban_integration_repository import IKanbanIntegrationRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.payment_repository import ISubscriptionPaymentRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.financing_portal_repository import (
    IFinancingActivityRepository,
    IFinancingDisbursementRepository,
    IFinancingDocumentRepository,
)
from app.domain.repositories.project_financing_repository import IProjectFinancingRepository
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.domain.repositories.report_repository import (
    IBankSubmissionRepository,
    IReportRepository,
    IReportShareRepository,
)
from app.domain.repositories.scraping_repository import IScrapingRepository
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.external.angola_api_client import AngolaApiClient
from app.infrastructure.geocoding.location_geocoder import LocationGeocoder
from app.infrastructure.excel.indicators_exporter import IndicatorsExcelExporter
from app.infrastructure.financial.monte_carlo_engine import NumpyMonteCarloEngine
from app.infrastructure.financial.sensitivity_engine import TornadoSensitivityEngine
from app.infrastructure.financial.viability_calculator import ViabilityCalculator
from app.infrastructure.bank.bank_api_client import BankApiClient
from app.infrastructure.auth.auth_rate_limiter import AuthRateLimiter
from app.infrastructure.auth.google_token_verifier import GoogleTokenVerifier
from app.infrastructure.email.smtp_email_service import SmtpEmailService
from app.infrastructure.payments.appy_pay_client import AppyPayClient
from app.infrastructure.pdf.report_generator import ReportPdfGenerator
from app.infrastructure.excel.openpyxl_parser import OpenpyxlExcelParser
from app.infrastructure.qrcode.qr_code_service import QRCodeService
from app.infrastructure.scraping.agt_nif_lookup import AgtNifLookupService
from app.infrastructure.scraping.angolan_bank_rate_scraper import AngolanBankRateScraper
from app.infrastructure.scraping.angolan_market_scrapers import build_default_market_scrapers
from app.infrastructure.scraping.scraping_orchestrator import ScrapingOrchestrator
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.infrastructure.security.sha256_hash_service import Sha256HashService
from app.infrastructure.supabase.admin_config_repository import (
    SupabaseBudgetTemplateRepository,
    SupabaseIntegrationSettingsRepository,
    SupabaseScrapingSourceAdminRepository,
    SupabaseSubscriptionRepository,
)
from app.infrastructure.supabase.platform_settings_repository import (
    SupabasePlatformSettingsRepository,
)
from app.infrastructure.supabase.access_log_repository import SupabaseAccessLogRepository
from app.infrastructure.supabase.analysis_repository import (
    SupabaseFinancialAnalysisRepository,
    SupabaseFinancialAssumptionsRepository,
    SupabaseMonteCarloRepository,
    SupabaseSectorBenchmarkRepository,
    SupabaseSensitivityRepository,
)
from app.infrastructure.supabase.audit_trail_repository import SupabaseAuditTrailRepository
from app.infrastructure.supabase.budget_repository import SupabaseBudgetRepository
from app.infrastructure.supabase.collaboration_repository import (
    SupabaseChatMessageRepository,
    SupabaseChatReadStateRepository,
    SupabaseKanbanTaskRepository,
    SupabaseProjectPresenceRepository,
    SupabaseTaskDependencyRepository,
)
from app.infrastructure.supabase.notification_repository import SupabaseNotificationRepository
from app.infrastructure.supabase.kanban_integration_repository import (
    SupabaseKanbanIntegrationRepository,
)
from app.infrastructure.supabase.client import create_supabase_client
from app.infrastructure.supabase.cost_item_repository import SupabaseCostItemRepository
from app.infrastructure.supabase.payment_repository import SupabaseSubscriptionPaymentRepository
from app.infrastructure.supabase.financing_portal_repository import (
    SupabaseFinancingActivityRepository,
    SupabaseFinancingDisbursementRepository,
    SupabaseFinancingDocumentRepository,
)
from app.infrastructure.supabase.billing_integration_repository import (
    SupabaseProjectBillingIntegrationRepository,
)
from app.infrastructure.supabase.project_financing_repository import (
    SupabaseProjectFinancingRepository,
)
from app.infrastructure.supabase.project_repository import SupabaseProjectRepository
from app.infrastructure.supabase.analyst_office_repository import SupabaseAnalystOfficeRepository
from app.infrastructure.supabase.project_share_repository import SupabaseProjectShareRepository
from app.infrastructure.supabase.report_repository import (
    SupabaseBankSubmissionRepository,
    SupabaseReportRepository,
    SupabaseReportShareRepository,
)
from app.infrastructure.supabase.scraping_repository import SupabaseScrapingRepository
from app.infrastructure.supabase.registration_invite_repository import (
    SupabaseRegistrationInviteRepository,
)
from app.infrastructure.supabase.user_repository import SupabaseUserRepository


@dataclass
class Container:
    config: Config
    user_repository: IUserRepository
    access_log_repository: IAccessLogRepository
    project_repository: IProjectRepository
    project_share_repository: IProjectShareRepository
    shared_project_capability_policy: SharedProjectCapabilityPolicy
    office_access_policy: OfficeAccessPolicy
    get_office_dashboard_use_case: GetOfficeDashboardUseCase
    list_office_members_use_case: ListOfficeMembersUseCase
    create_office_member_use_case: CreateOfficeMemberUseCase
    update_office_member_use_case: UpdateOfficeMemberUseCase
    archive_office_member_use_case: ArchiveOfficeMemberUseCase
    assign_office_member_projects_use_case: AssignOfficeMemberProjectsUseCase
    list_office_member_access_use_case: ListOfficeMemberAccessUseCase
    admin_list_offices_use_case: AdminListOfficesUseCase
    cost_item_repository: ICostItemRepository
    scraping_repository: IScrapingRepository
    budget_repository: IBudgetRepository
    audit_trail_repository: IAuditTrailRepository
    assumptions_repository: IFinancialAssumptionsRepository
    analysis_repository: IFinancialAnalysisRepository
    monte_carlo_repository: IMonteCarloRepository
    sensitivity_repository: ISensitivityRepository
    benchmark_repository: ISectorBenchmarkRepository
    password_hasher: IPasswordHasher
    token_service: ITokenService
    email_service: IEmailService
    hash_service: IHashService
    project_access_policy: ProjectAccessPolicy
    ingestion_access_policy: IngestionAccessPolicy
    analysis_access_policy: AnalysisAccessPolicy
    collaboration_access_policy: CollaborationAccessPolicy
    project_context_resolver: ProjectContextResolver
    kanban_task_repository: IKanbanTaskRepository
    task_dependency_repository: ITaskDependencyRepository
    chat_message_repository: IChatMessageRepository
    chat_read_state_repository: IChatReadStateRepository
    project_presence_repository: IProjectPresenceRepository
    notification_repository: INotificationRepository
    notification_service: NotificationService
    registration_policy_service: RegistrationPolicyService
    kanban_integration_repository: IKanbanIntegrationRepository
    kanban_board_service: KanbanBoardService
    kanban_task_service: KanbanTaskService

    # Auth
    login_use_case: LoginUseCase
    register_user_use_case: RegisterUserUseCase
    recover_password_use_case: RecoverPasswordUseCase
    reset_password_use_case: ResetPasswordUseCase
    refresh_token_use_case: RefreshTokenUseCase
    logout_use_case: LogoutUseCase
    get_current_user_use_case: GetCurrentUserUseCase
    update_user_preferences_use_case: UpdateUserPreferencesUseCase
    request_signup_otp_use_case: RequestSignupOtpUseCase
    verify_signup_otp_use_case: VerifySignupOtpUseCase
    resend_signup_otp_use_case: ResendSignupOtpUseCase
    google_auth_use_case: GoogleAuthUseCase
    get_registration_status_use_case: GetRegistrationStatusUseCase

    # Admin
    list_users_use_case: ListUsersUseCase
    get_user_use_case: GetUserUseCase
    update_user_use_case: UpdateUserUseCase
    update_user_role_use_case: UpdateUserRoleUseCase
    approve_user_use_case: ApproveUserUseCase
    extend_user_access_use_case: ExtendUserAccessUseCase
    get_access_logs_use_case: GetAccessLogsUseCase

    # Projects (M2)
    create_project_use_case: CreateProjectUseCase
    list_projects_use_case: ListProjectsUseCase
    get_project_use_case: GetProjectUseCase
    update_project_use_case: UpdateProjectUseCase
    delete_project_use_case: DeleteProjectUseCase
    share_project_use_case: ShareProjectUseCase
    list_project_shares_use_case: ListProjectSharesUseCase
    remove_project_share_use_case: RemoveProjectShareUseCase
    lookup_company_by_nif_use_case: LookupCompanyByNifUseCase
    list_financing_banks_use_case: ListFinancingBanksUseCase
    get_bank_discount_rate_use_case: GetBankDiscountRateUseCase
    list_bank_branches_use_case: ListBankBranchesUseCase
    validate_angola_bi_use_case: ValidateAngolaBiUseCase
    validate_angola_phone_use_case: ValidateAngolaPhoneUseCase
    generate_strategic_insights_use_case: GenerateStrategicInsightsUseCase
    get_sector_profile_use_case: GetSectorProfileUseCase
    extract_company_document_use_case: ExtractCompanyDocumentUseCase

    # Ingestion (M3)
    create_cost_item_use_case: CreateCostItemUseCase
    import_cost_items_excel_use_case: ImportCostItemsExcelUseCase
    list_cost_items_use_case: ListCostItemsUseCase
    update_cost_item_use_case: UpdateCostItemUseCase
    delete_cost_item_use_case: DeleteCostItemUseCase
    execute_scraping_use_case: ExecuteScrapingUseCase
    get_scraping_job_use_case: GetScrapingJobUseCase
    list_scraping_sources_use_case: ListScrapingSourcesUseCase
    select_supplier_use_case: SelectSupplierUseCase
    generate_budget_use_case: GenerateBudgetUseCase
    approve_budget_use_case: ApproveBudgetUseCase
    list_budgets_use_case: ListBudgetsUseCase
    get_budget_use_case: GetBudgetUseCase
    generate_proforma_use_case: GenerateProformaUseCase
    list_proformas_use_case: ListProformasUseCase
    get_audit_trail_use_case: GetAuditTrailUseCase
    verify_budget_use_case: VerifyBudgetUseCase
    preview_auto_ingestion_use_case: PreviewAutoIngestionUseCase
    run_auto_ingestion_use_case: RunAutoIngestionUseCase

    # Analysis (M4)
    calculate_indicators_use_case: CalculateIndicatorsUseCase
    list_analyses_use_case: ListAnalysesUseCase
    get_analysis_use_case: GetAnalysisUseCase
    run_monte_carlo_use_case: RunMonteCarloUseCase
    list_monte_carlo_use_case: ListMonteCarloUseCase
    run_sensitivity_use_case: RunSensitivityUseCase
    list_sensitivity_use_case: ListSensitivityUseCase
    compare_benchmarks_use_case: CompareBenchmarksUseCase
    export_indicators_use_case: ExportIndicatorsUseCase
    run_scenario_analysis_use_case: RunScenarioAnalysisUseCase

    # Collaboration (M5)
    create_task_use_case: CreateTaskUseCase
    list_tasks_use_case: ListTasksUseCase
    get_task_use_case: GetTaskUseCase
    update_task_use_case: UpdateTaskUseCase
    move_task_use_case: MoveTaskUseCase
    delete_task_use_case: DeleteTaskUseCase
    create_task_dependency_use_case: CreateTaskDependencyUseCase
    list_task_dependencies_use_case: ListTaskDependenciesUseCase
    delete_task_dependency_use_case: DeleteTaskDependencyUseCase
    send_chat_message_use_case: SendChatMessageUseCase
    list_chat_messages_use_case: ListChatMessagesUseCase
    get_kanban_integration_use_case: GetKanbanIntegrationUseCase
    sync_kanban_board_use_case: SyncKanbanBoardUseCase

    # Notifications & chat realtime
    list_notifications_use_case: ListNotificationsUseCase
    mark_notification_read_use_case: MarkNotificationReadUseCase
    mark_all_notifications_read_use_case: MarkAllNotificationsReadUseCase
    poll_chat_use_case: PollChatUseCase
    mark_chat_read_use_case: MarkChatReadUseCase
    chat_presence_use_case: ChatPresenceUseCase

    # Reports (M6)
    report_repository: IReportRepository
    report_share_repository: IReportShareRepository
    bank_submission_repository: IBankSubmissionRepository
    report_access_policy: ReportAccessPolicy
    generate_report_use_case: GenerateReportUseCase
    list_reports_use_case: ListReportsUseCase
    get_report_use_case: GetReportUseCase
    download_report_use_case: DownloadReportUseCase
    print_report_use_case: PrintReportUseCase
    send_report_email_use_case: SendReportEmailUseCase
    share_report_whatsapp_use_case: ShareReportWhatsAppUseCase
    submit_report_to_bank_use_case: SubmitReportToBankUseCase
    get_shared_report_use_case: GetSharedReportUseCase
    verify_report_use_case: VerifyReportUseCase

    # Financier portal
    project_financing_repository: IProjectFinancingRepository
    financier_access_policy: FinancierAccessPolicy
    create_project_financing_use_case: CreateProjectFinancingUseCase
    decide_project_financing_use_case: DecideProjectFinancingUseCase
    list_project_financings_use_case: ListProjectFinancingsUseCase
    list_financier_pending_approvals_use_case: ListFinancierPendingApprovalsUseCase
    list_financier_portfolio_use_case: ListFinancierPortfolioUseCase
    get_financier_monitoring_use_case: GetFinancierMonitoringUseCase
    get_financier_dashboard_use_case: GetFinancierDashboardUseCase
    list_financier_alerts_use_case: ListFinancierAlertsUseCase
    list_financier_disbursements_use_case: ListFinancierDisbursementsUseCase
    list_financier_documents_use_case: ListFinancierDocumentsUseCase
    list_financier_activity_use_case: ListFinancierActivityUseCase
    create_financing_disbursement_use_case: CreateFinancingDisbursementUseCase
    update_financing_disbursement_use_case: UpdateFinancingDisbursementUseCase
    create_financing_document_use_case: CreateFinancingDocumentUseCase
    validate_financing_document_use_case: ValidateFinancingDocumentUseCase
    export_financier_portfolio_report_use_case: ExportFinancierPortfolioReportUseCase
    get_project_billing_integration_use_case: GetProjectBillingIntegrationUseCase
    configure_project_billing_integration_use_case: ConfigureProjectBillingIntegrationUseCase
    sync_project_billing_integration_use_case: SyncProjectBillingIntegrationUseCase
    list_financier_billing_integrations_use_case: ListFinancierBillingIntegrationsUseCase
    regenerate_project_billing_api_key_use_case: RegenerateProjectBillingApiKeyUseCase
    sync_billing_via_api_key_use_case: SyncBillingViaApiKeyUseCase
    export_financier_credit_report_use_case: ExportFinancierCreditReportUseCase

    # Admin config (M7)
    admin_access_policy: AdminAccessPolicy
    integration_config_service: IntegrationConfigService
    subscription_service: SubscriptionService
    list_scraping_sources_admin_use_case: ListScrapingSourcesAdminUseCase
    create_scraping_source_use_case: CreateScrapingSourceUseCase
    update_scraping_source_use_case: UpdateScrapingSourceUseCase
    delete_scraping_source_use_case: DeleteScrapingSourceUseCase
    list_integrations_use_case: ListIntegrationsUseCase
    get_integration_use_case: GetIntegrationUseCase
    update_integration_use_case: UpdateIntegrationUseCase
    test_integration_use_case: TestIntegrationUseCase
    list_budget_templates_use_case: ListBudgetTemplatesUseCase
    create_budget_template_use_case: CreateBudgetTemplateUseCase
    update_budget_template_use_case: UpdateBudgetTemplateUseCase
    set_default_budget_template_use_case: SetDefaultBudgetTemplateUseCase
    delete_budget_template_use_case: DeleteBudgetTemplateUseCase
    get_global_audit_trail_use_case: GetGlobalAuditTrailUseCase
    list_subscription_plans_use_case: ListSubscriptionPlansUseCase
    create_subscription_plan_use_case: CreateSubscriptionPlanUseCase
    update_subscription_plan_use_case: UpdateSubscriptionPlanUseCase
    delete_subscription_plan_use_case: DeleteSubscriptionPlanUseCase
    list_user_subscriptions_use_case: ListUserSubscriptionsUseCase
    assign_user_subscription_use_case: AssignUserSubscriptionUseCase
    update_user_subscription_status_use_case: UpdateUserSubscriptionStatusUseCase
    get_billing_overview_use_case: GetBillingOverviewUseCase
    list_admin_payments_use_case: ListAdminPaymentsUseCase
    list_admin_customers_use_case: ListAdminCustomersUseCase
    sync_subscription_plans_use_case: SyncSubscriptionPlansUseCase
    manage_pricing_promotion_use_case: ManagePricingPromotionUseCase
    list_public_plans_use_case: ListPublicPlansUseCase
    prepare_checkout_use_case: PrepareCheckoutUseCase
    get_my_subscription_use_case: GetMySubscriptionUseCase
    subscribe_to_plan_use_case: SubscribeToPlanUseCase
    initiate_appypay_payment_use_case: InitiateAppyPayPaymentUseCase
    poll_appypay_payment_use_case: PollAppyPayPaymentUseCase
    mock_appypay_reference_use_case: MockAppyPayReferenceUseCase
    appy_pay_client: AppyPayClient


def _create_trello_provider(config: Config):
    """Inicializa Trello apenas se credenciais e dependência requests existirem."""
    if not config.TRELLO_API_KEY or not config.TRELLO_API_TOKEN:
        return None
    try:
        from app.infrastructure.kanban.trello_client import TrelloClient
        from app.infrastructure.kanban.trello_provider import TrelloKanbanProvider
    except ImportError as exc:
        import logging

        logging.getLogger(__name__).warning(
            "Integração Trello indisponível: instale dependências com "
            "'pip install -r requirements.txt' (%s)",
            exc,
        )
        return None
    return TrelloKanbanProvider(TrelloClient(config.TRELLO_API_KEY, config.TRELLO_API_TOKEN))


def build_container(config: Config | None = None) -> Container:
    config = config or Config()

    supabase = create_supabase_client(config)
    user_repository = SupabaseUserRepository(supabase)
    access_log_repository = SupabaseAccessLogRepository(supabase)
    project_repository = SupabaseProjectRepository(supabase)
    project_share_repository = SupabaseProjectShareRepository(supabase)
    analyst_office_repository = SupabaseAnalystOfficeRepository(supabase)
    shared_project_capability_policy = SharedProjectCapabilityPolicy(project_share_repository)
    office_access_policy = OfficeAccessPolicy()
    cost_item_repository = SupabaseCostItemRepository(supabase)
    scraping_repository = SupabaseScrapingRepository(supabase)
    budget_repository = SupabaseBudgetRepository(supabase)
    audit_trail_repository = SupabaseAuditTrailRepository(supabase)
    assumptions_repository = SupabaseFinancialAssumptionsRepository(supabase)
    analysis_repository = SupabaseFinancialAnalysisRepository(supabase)
    monte_carlo_repository = SupabaseMonteCarloRepository(supabase)
    sensitivity_repository = SupabaseSensitivityRepository(supabase)
    benchmark_repository = SupabaseSectorBenchmarkRepository(supabase)
    kanban_task_repository = SupabaseKanbanTaskRepository(supabase)
    task_dependency_repository = SupabaseTaskDependencyRepository(supabase)
    chat_message_repository = SupabaseChatMessageRepository(supabase)
    chat_read_state_repository = SupabaseChatReadStateRepository(supabase)
    project_presence_repository = SupabaseProjectPresenceRepository(supabase)
    notification_repository = SupabaseNotificationRepository(supabase)
    kanban_integration_repository = SupabaseKanbanIntegrationRepository(supabase)
    report_repository = SupabaseReportRepository(supabase)
    report_share_repository = SupabaseReportShareRepository(supabase)
    bank_submission_repository = SupabaseBankSubmissionRepository(supabase)
    project_financing_repository = SupabaseProjectFinancingRepository(supabase)
    financing_disbursement_repository = SupabaseFinancingDisbursementRepository(supabase)
    financing_document_repository = SupabaseFinancingDocumentRepository(supabase)
    financing_activity_repository = SupabaseFinancingActivityRepository(supabase)
    billing_integration_repository = SupabaseProjectBillingIntegrationRepository(supabase)
    financier_access_policy = FinancierAccessPolicy(shared_project_capability_policy)
    financier_portfolio_loader = FinancierPortfolioLoader(
        user_repository,
        project_repository,
        project_financing_repository,
        cost_item_repository,
        kanban_task_repository,
        financing_disbursement_repository,
        financing_document_repository,
        financier_access_policy,
        analysis_repository,
        billing_integration_repository,
    )
    get_financier_project_detail_use_case = GetFinancierProjectDetailUseCase(
        user_repository,
        project_repository,
        project_financing_repository,
        cost_item_repository,
        kanban_task_repository,
        financing_disbursement_repository,
        financing_document_repository,
        financing_activity_repository,
        financier_access_policy,
        analysis_repository,
        billing_integration_repository,
    )
    get_financier_dashboard_use_case = GetFinancierDashboardUseCase(
        financier_portfolio_loader,
        financing_activity_repository,
    )
    scraping_source_admin_repository = SupabaseScrapingSourceAdminRepository(supabase)
    integration_settings_repository = SupabaseIntegrationSettingsRepository(supabase)
    budget_template_repository = SupabaseBudgetTemplateRepository(supabase)
    subscription_repository = SupabaseSubscriptionRepository(supabase)
    payment_repository = SupabaseSubscriptionPaymentRepository(supabase)
    platform_settings_repository = SupabasePlatformSettingsRepository(supabase)
    commercial_pricing_service = CommercialPricingService(platform_settings_repository)
    appy_pay_client = AppyPayClient(config)

    trello_provider = _create_trello_provider(config)

    kanban_board_service = KanbanBoardService(
        config, kanban_integration_repository, trello_provider
    )
    kanban_task_service = KanbanTaskService(
        kanban_task_repository, kanban_board_service, trello_provider
    )

    password_hasher = BcryptPasswordHasher()
    token_service = JwtTokenService(config)
    hash_service = Sha256HashService()
    hash_builder = CostItemHashBuilder(hash_service)
    excel_parser = OpenpyxlExcelParser()
    qr_service = QRCodeService()
    scraping_orchestrator = ScrapingOrchestrator(build_default_market_scrapers())
    sector_item_catalog = SectorItemCatalog()
    sector_profile_service = SectorProfileService(
        sector_item_catalog,
        benchmark_repository,
    )
    nif_lookup_service = AgtNifLookupService()
    angola_api_client = AngolaApiClient(base_url=config.ANGOLA_API_BASE_URL)
    bank_rate_scraper = AngolanBankRateScraper()

    viability_calculator = ViabilityCalculator()
    monte_carlo_engine = NumpyMonteCarloEngine(viability_calculator)
    sensitivity_engine = TornadoSensitivityEngine(viability_calculator)
    indicators_exporter = IndicatorsExcelExporter()
    analysis_context_builder = AnalysisContextBuilder()
    strategic_insights_service = StrategicInsightsService()
    company_document_extractor = CompanyDocumentExtractor()

    project_access_policy = ProjectAccessPolicy()
    ingestion_access_policy = IngestionAccessPolicy(
        project_access_policy, shared_project_capability_policy
    )
    analysis_access_policy = AnalysisAccessPolicy(
        project_access_policy, shared_project_capability_policy
    )
    collaboration_access_policy = CollaborationAccessPolicy(
        project_access_policy,
        project_repository,
        user_repository,
        shared_project_capability_policy,
    )
    report_access_policy = ReportAccessPolicy(
        project_access_policy, shared_project_capability_policy
    )
    report_data_aggregator = ReportDataAggregator(
        project_repository,
        user_repository,
        cost_item_repository,
        budget_repository,
        analysis_repository,
        monte_carlo_repository,
        sensitivity_repository,
        benchmark_repository,
        audit_trail_repository,
        kanban_task_repository,
    )
    report_prerequisites_validator = ReportPrerequisitesValidator(
        project_repository,
        cost_item_repository,
        budget_repository,
        analysis_repository,
        monte_carlo_repository,
    )
    pdf_generator = ReportPdfGenerator()
    admin_access_policy = AdminAccessPolicy(user_repository)
    integration_config_service = IntegrationConfigService(
        integration_settings_repository, config
    )
    email_service = SmtpEmailService(config, integration_config_service)
    subscription_service = SubscriptionService(subscription_repository)
    user_access_enforcement = UserAccessEnforcementService(
        user_repository, subscription_repository
    )
    notification_service = NotificationService(notification_repository, user_repository)
    account_role_service = AccountRoleService(user_repository, subscription_repository)
    registration_invite_repository = SupabaseRegistrationInviteRepository(supabase)
    registration_policy_service = RegistrationPolicyService(config, registration_invite_repository)
    auth_rate_limiter = AuthRateLimiter(
        max_attempts=config.AUTH_RATE_LIMIT_MAX,
        window_seconds=config.AUTH_RATE_LIMIT_WINDOW_SECONDS,
    )
    registration_invite_fulfillment = RegistrationInviteFulfillmentService(
        registration_invite_repository,
        project_repository,
        project_share_repository,
        user_repository,
        notification_service,
    )
    google_token_verifier = GoogleTokenVerifier(config)
    bank_api_client = BankApiClient(config, integration_config_service)
    task_dependency_validator = TaskDependencyValidator(
        kanban_task_repository, task_dependency_repository
    )
    context_resolver = ProjectContextResolver(
        user_repository,
        project_repository,
        project_access_policy,
        ingestion_access_policy,
    )

    return Container(
        config=config,
        user_repository=user_repository,
        access_log_repository=access_log_repository,
        project_repository=project_repository,
        project_share_repository=project_share_repository,
        shared_project_capability_policy=shared_project_capability_policy,
        office_access_policy=office_access_policy,
        cost_item_repository=cost_item_repository,
        scraping_repository=scraping_repository,
        budget_repository=budget_repository,
        audit_trail_repository=audit_trail_repository,
        assumptions_repository=assumptions_repository,
        analysis_repository=analysis_repository,
        monte_carlo_repository=monte_carlo_repository,
        sensitivity_repository=sensitivity_repository,
        benchmark_repository=benchmark_repository,
        password_hasher=password_hasher,
        token_service=token_service,
        email_service=email_service,
        hash_service=hash_service,
        project_access_policy=project_access_policy,
        ingestion_access_policy=ingestion_access_policy,
        analysis_access_policy=analysis_access_policy,
        collaboration_access_policy=collaboration_access_policy,
        project_context_resolver=context_resolver,
        kanban_task_repository=kanban_task_repository,
        task_dependency_repository=task_dependency_repository,
        chat_message_repository=chat_message_repository,
        chat_read_state_repository=chat_read_state_repository,
        project_presence_repository=project_presence_repository,
        notification_repository=notification_repository,
        notification_service=notification_service,
        registration_policy_service=registration_policy_service,
        kanban_integration_repository=kanban_integration_repository,
        kanban_board_service=kanban_board_service,
        kanban_task_service=kanban_task_service,
        login_use_case=LoginUseCase(
            user_repository,
            access_log_repository,
            password_hasher,
            token_service,
            account_role_service,
            user_access_enforcement,
            auth_rate_limiter,
            config,
        ),
        register_user_use_case=RegisterUserUseCase(
            user_repository, access_log_repository, password_hasher
        ),
        recover_password_use_case=RecoverPasswordUseCase(
            user_repository, access_log_repository, token_service, email_service, config
        ),
        reset_password_use_case=ResetPasswordUseCase(
            user_repository, access_log_repository, password_hasher, token_service
        ),
        refresh_token_use_case=RefreshTokenUseCase(
            user_repository,
            access_log_repository,
            token_service,
            account_role_service,
            user_access_enforcement,
            config,
        ),
        logout_use_case=LogoutUseCase(user_repository, access_log_repository, token_service),
        get_current_user_use_case=GetCurrentUserUseCase(
            user_repository, account_role_service, user_access_enforcement
        ),
        update_user_preferences_use_case=UpdateUserPreferencesUseCase(user_repository),
        request_signup_otp_use_case=RequestSignupOtpUseCase(
            user_repository,
            access_log_repository,
            password_hasher,
            token_service,
            email_service,
            registration_policy_service,
            auth_rate_limiter,
            config,
        ),
        verify_signup_otp_use_case=VerifySignupOtpUseCase(
            user_repository,
            access_log_repository,
            subscription_repository,
            token_service,
            registration_policy_service,
            registration_invite_fulfillment,
            notification_service,
            auth_rate_limiter,
            config,
        ),
        resend_signup_otp_use_case=ResendSignupOtpUseCase(
            user_repository,
            access_log_repository,
            token_service,
            email_service,
            config,
        ),
        google_auth_use_case=GoogleAuthUseCase(
            user_repository,
            subscription_repository,
            access_log_repository,
            token_service,
            account_role_service,
            google_token_verifier,
            registration_policy_service,
            registration_invite_fulfillment,
            notification_service,
            auth_rate_limiter,
            user_access_enforcement,
            config,
        ),
        get_registration_status_use_case=GetRegistrationStatusUseCase(
            user_repository,
            auth_rate_limiter,
        ),
        list_users_use_case=ListUsersUseCase(user_repository),
        get_user_use_case=GetUserUseCase(user_repository),
        update_user_use_case=UpdateUserUseCase(
            user_repository, access_log_repository, subscription_repository
        ),
        update_user_role_use_case=UpdateUserRoleUseCase(
            user_repository, access_log_repository
        ),
        approve_user_use_case=ApproveUserUseCase(
            user_repository,
            subscription_repository,
            access_log_repository,
            notification_service,
        ),
        extend_user_access_use_case=ExtendUserAccessUseCase(
            user_repository,
            subscription_repository,
            access_log_repository,
            notification_service,
        ),
        get_access_logs_use_case=GetAccessLogsUseCase(
            user_repository, access_log_repository
        ),
        create_project_use_case=CreateProjectUseCase(
            user_repository,
            project_repository,
            access_log_repository,
            project_access_policy,
            subscription_service,
            LocationGeocoder(google_maps_api_key=config.GOOGLE_MAPS_API_KEY),
            angola_api_client,
        ),
        list_projects_use_case=ListProjectsUseCase(
            user_repository, project_repository, project_share_repository, project_access_policy
        ),
        get_project_use_case=GetProjectUseCase(
            user_repository,
            project_repository,
            project_share_repository,
            project_access_policy,
            cost_item_repository,
        ),
        update_project_use_case=UpdateProjectUseCase(
            user_repository,
            project_repository,
            access_log_repository,
            project_access_policy,
            cost_item_repository,
            LocationGeocoder(google_maps_api_key=config.GOOGLE_MAPS_API_KEY),
            shared_project_capability_policy,
        ),
        delete_project_use_case=DeleteProjectUseCase(
            user_repository, project_repository, access_log_repository, project_access_policy
        ),
        share_project_use_case=ShareProjectUseCase(
            user_repository,
            project_repository,
            project_share_repository,
            access_log_repository,
            project_access_policy,
            registration_policy_service,
            subscription_service,
            notification_service,
        ),
        list_project_shares_use_case=ListProjectSharesUseCase(
            user_repository, project_repository, project_share_repository, project_access_policy
        ),
        remove_project_share_use_case=RemoveProjectShareUseCase(
            user_repository,
            project_repository,
            project_share_repository,
            access_log_repository,
            project_access_policy,
        ),
        get_office_dashboard_use_case=GetOfficeDashboardUseCase(
            user_repository,
            project_repository,
            project_share_repository,
            analyst_office_repository,
            office_access_policy,
        ),
        list_office_members_use_case=ListOfficeMembersUseCase(
            user_repository,
            analyst_office_repository,
            project_share_repository,
            office_access_policy,
        ),
        create_office_member_use_case=CreateOfficeMemberUseCase(
            user_repository,
            analyst_office_repository,
            office_access_policy,
        ),
        update_office_member_use_case=UpdateOfficeMemberUseCase(
            user_repository,
            analyst_office_repository,
            office_access_policy,
        ),
        archive_office_member_use_case=ArchiveOfficeMemberUseCase(
            user_repository,
            analyst_office_repository,
            office_access_policy,
        ),
        assign_office_member_projects_use_case=AssignOfficeMemberProjectsUseCase(
            user_repository,
            project_repository,
            analyst_office_repository,
            project_share_repository,
            office_access_policy,
            project_access_policy,
            ShareProjectUseCase(
                user_repository,
                project_repository,
                project_share_repository,
                access_log_repository,
                project_access_policy,
                registration_policy_service,
                subscription_service,
                notification_service,
            ),
        ),
        list_office_member_access_use_case=ListOfficeMemberAccessUseCase(
            user_repository,
            project_repository,
            analyst_office_repository,
            project_share_repository,
            office_access_policy,
        ),
        admin_list_offices_use_case=AdminListOfficesUseCase(
            user_repository,
            analyst_office_repository,
            project_repository,
        ),
        lookup_company_by_nif_use_case=LookupCompanyByNifUseCase(nif_lookup_service),
        list_financing_banks_use_case=ListFinancingBanksUseCase(bank_rate_scraper),
        get_bank_discount_rate_use_case=GetBankDiscountRateUseCase(bank_rate_scraper),
        list_bank_branches_use_case=ListBankBranchesUseCase(),
        validate_angola_bi_use_case=ValidateAngolaBiUseCase(angola_api_client),
        validate_angola_phone_use_case=ValidateAngolaPhoneUseCase(angola_api_client),
        generate_strategic_insights_use_case=GenerateStrategicInsightsUseCase(
            context_resolver,
            project_repository,
            strategic_insights_service,
        ),
        get_sector_profile_use_case=GetSectorProfileUseCase(
            context_resolver,
            sector_profile_service,
        ),
        extract_company_document_use_case=ExtractCompanyDocumentUseCase(
            company_document_extractor,
        ),
        create_cost_item_use_case=CreateCostItemUseCase(
            context_resolver,
            cost_item_repository,
            audit_trail_repository,
            hash_builder,
            nif_lookup_service,
        ),
        import_cost_items_excel_use_case=ImportCostItemsExcelUseCase(
            context_resolver,
            cost_item_repository,
            audit_trail_repository,
            hash_builder,
            hash_service,
            excel_parser,
        ),
        list_cost_items_use_case=ListCostItemsUseCase(context_resolver, cost_item_repository),
        update_cost_item_use_case=UpdateCostItemUseCase(
            context_resolver,
            cost_item_repository,
            audit_trail_repository,
            hash_builder,
        ),
        delete_cost_item_use_case=DeleteCostItemUseCase(
            context_resolver, cost_item_repository, audit_trail_repository, budget_repository
        ),
        execute_scraping_use_case=ExecuteScrapingUseCase(
            context_resolver,
            scraping_repository,
            audit_trail_repository,
            scraping_orchestrator,
            hash_service,
            subscription_service,
        ),
        get_scraping_job_use_case=GetScrapingJobUseCase(context_resolver, scraping_repository),
        list_scraping_sources_use_case=ListScrapingSourcesUseCase(scraping_repository),
        select_supplier_use_case=SelectSupplierUseCase(
            context_resolver,
            scraping_repository,
            cost_item_repository,
            audit_trail_repository,
            hash_builder,
        ),
        generate_budget_use_case=GenerateBudgetUseCase(
            context_resolver,
            cost_item_repository,
            budget_repository,
            audit_trail_repository,
            hash_service,
            qr_service,
            config,
            budget_template_repository,
        ),
        approve_budget_use_case=ApproveBudgetUseCase(
            context_resolver, budget_repository, project_repository, audit_trail_repository
        ),
        list_budgets_use_case=ListBudgetsUseCase(context_resolver, budget_repository),
        get_budget_use_case=GetBudgetUseCase(context_resolver, budget_repository),
        generate_proforma_use_case=GenerateProformaUseCase(
            context_resolver,
            budget_repository,
            audit_trail_repository,
            hash_service,
            qr_service,
            config,
        ),
        list_proformas_use_case=ListProformasUseCase(context_resolver, budget_repository),
        get_audit_trail_use_case=GetAuditTrailUseCase(
            context_resolver, audit_trail_repository
        ),
        verify_budget_use_case=VerifyBudgetUseCase(
            budget_repository, project_repository, cost_item_repository
        ),
        preview_auto_ingestion_use_case=PreviewAutoIngestionUseCase(
            context_resolver, sector_item_catalog
        ),
        run_auto_ingestion_use_case=RunAutoIngestionUseCase(
            context_resolver,
            sector_item_catalog,
            scraping_orchestrator,
            scraping_repository,
            cost_item_repository,
            budget_repository,
            audit_trail_repository,
            hash_builder,
            hash_service,
            qr_service,
            config,
            subscription_service,
        ),
        calculate_indicators_use_case=CalculateIndicatorsUseCase(
            context_resolver,
            analysis_access_policy,
            analysis_context_builder,
            cost_item_repository,
            assumptions_repository,
            analysis_repository,
            viability_calculator,
            hash_service,
        ),
        list_analyses_use_case=ListAnalysesUseCase(
            context_resolver, analysis_access_policy, analysis_repository
        ),
        get_analysis_use_case=GetAnalysisUseCase(
            context_resolver, analysis_access_policy, analysis_repository
        ),
        run_monte_carlo_use_case=RunMonteCarloUseCase(
            context_resolver,
            analysis_access_policy,
            analysis_context_builder,
            cost_item_repository,
            assumptions_repository,
            analysis_repository,
            monte_carlo_repository,
            monte_carlo_engine,
            subscription_service,
        ),
        list_monte_carlo_use_case=ListMonteCarloUseCase(
            context_resolver, analysis_access_policy, monte_carlo_repository
        ),
        run_sensitivity_use_case=RunSensitivityUseCase(
            context_resolver,
            analysis_access_policy,
            analysis_context_builder,
            cost_item_repository,
            assumptions_repository,
            analysis_repository,
            sensitivity_repository,
            sensitivity_engine,
            subscription_service,
        ),
        list_sensitivity_use_case=ListSensitivityUseCase(
            context_resolver, analysis_access_policy, sensitivity_repository
        ),
        compare_benchmarks_use_case=CompareBenchmarksUseCase(
            context_resolver,
            analysis_access_policy,
            benchmark_repository,
            analysis_repository,
        ),
        export_indicators_use_case=ExportIndicatorsUseCase(
            context_resolver,
            analysis_access_policy,
            analysis_repository,
            indicators_exporter,
            cost_item_repository,
            sensitivity_repository,
        ),
        run_scenario_analysis_use_case=RunScenarioAnalysisUseCase(
            context_resolver,
            analysis_access_policy,
            analysis_context_builder,
            project_repository,
            cost_item_repository,
            viability_calculator,
            subscription_service,
        ),
        create_task_use_case=CreateTaskUseCase(
            context_resolver,
            collaboration_access_policy,
            kanban_task_repository,
            kanban_task_service,
        ),
        list_tasks_use_case=ListTasksUseCase(
            context_resolver,
            collaboration_access_policy,
            kanban_task_repository,
            kanban_task_service,
            kanban_board_service,
        ),
        get_task_use_case=GetTaskUseCase(
            context_resolver, collaboration_access_policy, kanban_task_repository
        ),
        update_task_use_case=UpdateTaskUseCase(
            context_resolver,
            collaboration_access_policy,
            kanban_task_repository,
            kanban_task_service,
        ),
        move_task_use_case=MoveTaskUseCase(
            context_resolver,
            collaboration_access_policy,
            kanban_task_repository,
            kanban_task_service,
            task_dependency_validator,
        ),
        delete_task_use_case=DeleteTaskUseCase(
            context_resolver,
            collaboration_access_policy,
            kanban_task_repository,
            kanban_task_service,
        ),
        create_task_dependency_use_case=CreateTaskDependencyUseCase(
            context_resolver,
            collaboration_access_policy,
            task_dependency_repository,
            task_dependency_validator,
        ),
        list_task_dependencies_use_case=ListTaskDependenciesUseCase(
            context_resolver, collaboration_access_policy, task_dependency_repository
        ),
        delete_task_dependency_use_case=DeleteTaskDependencyUseCase(
            context_resolver, collaboration_access_policy, task_dependency_repository
        ),
        send_chat_message_use_case=SendChatMessageUseCase(
            context_resolver,
            collaboration_access_policy,
            chat_message_repository,
            user_repository,
            project_share_repository,
            notification_service,
        ),
        list_chat_messages_use_case=ListChatMessagesUseCase(
            context_resolver, collaboration_access_policy, chat_message_repository, user_repository
        ),
        poll_chat_use_case=PollChatUseCase(
            context_resolver,
            collaboration_access_policy,
            chat_message_repository,
            chat_read_state_repository,
            project_presence_repository,
            user_repository,
        ),
        mark_chat_read_use_case=MarkChatReadUseCase(
            context_resolver,
            collaboration_access_policy,
            chat_read_state_repository,
        ),
        chat_presence_use_case=ChatPresenceUseCase(
            context_resolver,
            collaboration_access_policy,
            project_presence_repository,
            user_repository,
        ),
        list_notifications_use_case=ListNotificationsUseCase(notification_repository),
        mark_notification_read_use_case=MarkNotificationReadUseCase(notification_repository),
        mark_all_notifications_read_use_case=MarkAllNotificationsReadUseCase(notification_repository),
        get_kanban_integration_use_case=GetKanbanIntegrationUseCase(
            context_resolver, collaboration_access_policy, kanban_board_service
        ),
        sync_kanban_board_use_case=SyncKanbanBoardUseCase(
            context_resolver,
            collaboration_access_policy,
            kanban_board_service,
            kanban_task_service,
        ),
        report_repository=report_repository,
        report_share_repository=report_share_repository,
        bank_submission_repository=bank_submission_repository,
        report_access_policy=report_access_policy,
        generate_report_use_case=GenerateReportUseCase(
            context_resolver,
            report_access_policy,
            report_data_aggregator,
            report_prerequisites_validator,
            report_repository,
            pdf_generator,
            hash_service,
            qr_service,
            audit_trail_repository,
            config,
            subscription_service,
            notification_service,
            project_share_repository,
        ),
        list_reports_use_case=ListReportsUseCase(
            context_resolver, report_access_policy, report_repository
        ),
        get_report_use_case=GetReportUseCase(
            context_resolver, report_access_policy, report_repository
        ),
        download_report_use_case=DownloadReportUseCase(
            context_resolver, report_access_policy, report_repository
        ),
        print_report_use_case=PrintReportUseCase(
            context_resolver,
            report_access_policy,
            report_repository,
            audit_trail_repository,
        ),
        send_report_email_use_case=SendReportEmailUseCase(
            context_resolver,
            report_access_policy,
            report_repository,
            email_service,
            audit_trail_repository,
        ),
        share_report_whatsapp_use_case=ShareReportWhatsAppUseCase(
            context_resolver,
            report_access_policy,
            report_repository,
            report_share_repository,
            audit_trail_repository,
            config,
        ),
        submit_report_to_bank_use_case=SubmitReportToBankUseCase(
            context_resolver,
            report_access_policy,
            report_repository,
            bank_submission_repository,
            bank_api_client,
            audit_trail_repository,
            subscription_service,
        ),
        get_shared_report_use_case=GetSharedReportUseCase(
            report_share_repository, report_repository
        ),
        verify_report_use_case=VerifyReportUseCase(report_repository),
        admin_access_policy=admin_access_policy,
        integration_config_service=integration_config_service,
        subscription_service=subscription_service,
        list_scraping_sources_admin_use_case=ListScrapingSourcesAdminUseCase(
            admin_access_policy, scraping_source_admin_repository
        ),
        create_scraping_source_use_case=CreateScrapingSourceUseCase(
            admin_access_policy, scraping_source_admin_repository, access_log_repository
        ),
        update_scraping_source_use_case=UpdateScrapingSourceUseCase(
            admin_access_policy, scraping_source_admin_repository, access_log_repository
        ),
        delete_scraping_source_use_case=DeleteScrapingSourceUseCase(
            admin_access_policy, scraping_source_admin_repository, access_log_repository
        ),
        list_integrations_use_case=ListIntegrationsUseCase(
            admin_access_policy, integration_settings_repository
        ),
        get_integration_use_case=GetIntegrationUseCase(
            admin_access_policy, integration_settings_repository
        ),
        update_integration_use_case=UpdateIntegrationUseCase(
            admin_access_policy,
            integration_settings_repository,
            integration_config_service,
            access_log_repository,
        ),
        test_integration_use_case=TestIntegrationUseCase(
            admin_access_policy, integration_config_service
        ),
        list_budget_templates_use_case=ListBudgetTemplatesUseCase(
            admin_access_policy, budget_template_repository
        ),
        create_budget_template_use_case=CreateBudgetTemplateUseCase(
            admin_access_policy, budget_template_repository, access_log_repository
        ),
        update_budget_template_use_case=UpdateBudgetTemplateUseCase(
            admin_access_policy, budget_template_repository, access_log_repository
        ),
        set_default_budget_template_use_case=SetDefaultBudgetTemplateUseCase(
            admin_access_policy, budget_template_repository, access_log_repository
        ),
        delete_budget_template_use_case=DeleteBudgetTemplateUseCase(
            admin_access_policy, budget_template_repository, access_log_repository
        ),
        get_global_audit_trail_use_case=GetGlobalAuditTrailUseCase(
            admin_access_policy, audit_trail_repository
        ),
        list_subscription_plans_use_case=ListSubscriptionPlansUseCase(
            admin_access_policy, subscription_repository
        ),
        create_subscription_plan_use_case=CreateSubscriptionPlanUseCase(
            admin_access_policy, subscription_repository, access_log_repository
        ),
        update_subscription_plan_use_case=UpdateSubscriptionPlanUseCase(
            admin_access_policy, subscription_repository, access_log_repository
        ),
        delete_subscription_plan_use_case=DeleteSubscriptionPlanUseCase(
            admin_access_policy, subscription_repository, access_log_repository
        ),
        list_user_subscriptions_use_case=ListUserSubscriptionsUseCase(
            admin_access_policy, subscription_repository, user_repository
        ),
        assign_user_subscription_use_case=AssignUserSubscriptionUseCase(
            admin_access_policy,
            subscription_repository,
            user_repository,
            access_log_repository,
        ),
        update_user_subscription_status_use_case=UpdateUserSubscriptionStatusUseCase(
            admin_access_policy, subscription_repository, access_log_repository
        ),
        get_billing_overview_use_case=GetBillingOverviewUseCase(
            admin_access_policy,
            subscription_repository,
            payment_repository,
            user_repository,
        ),
        list_admin_payments_use_case=ListAdminPaymentsUseCase(
            admin_access_policy, payment_repository, user_repository
        ),
        list_admin_customers_use_case=ListAdminCustomersUseCase(
            admin_access_policy,
            user_repository,
            subscription_repository,
            payment_repository,
        ),
        sync_subscription_plans_use_case=SyncSubscriptionPlansUseCase(
            admin_access_policy, subscription_repository, access_log_repository
        ),
        manage_pricing_promotion_use_case=ManagePricingPromotionUseCase(
            admin_access_policy,
            platform_settings_repository,
            access_log_repository,
        ),
        list_public_plans_use_case=ListPublicPlansUseCase(
            subscription_repository, commercial_pricing_service
        ),
        prepare_checkout_use_case=PrepareCheckoutUseCase(
            subscription_repository, commercial_pricing_service
        ),
        get_my_subscription_use_case=GetMySubscriptionUseCase(
            subscription_repository, subscription_service, commercial_pricing_service
        ),
        subscribe_to_plan_use_case=SubscribeToPlanUseCase(
            subscription_repository, commercial_pricing_service
        ),
        initiate_appypay_payment_use_case=InitiateAppyPayPaymentUseCase(
            subscription_repository,
            payment_repository,
            appy_pay_client,
            commercial_pricing_service,
            sandbox=config.APPYPAY_SANDBOX,
        ),
        poll_appypay_payment_use_case=PollAppyPayPaymentUseCase(
            subscription_repository,
            payment_repository,
            appy_pay_client,
            commercial_pricing_service,
            sandbox=config.APPYPAY_SANDBOX,
        ),
        mock_appypay_reference_use_case=MockAppyPayReferenceUseCase(
            subscription_repository,
            payment_repository,
            appy_pay_client,
            commercial_pricing_service,
            sandbox=config.APPYPAY_SANDBOX,
        ),
        appy_pay_client=appy_pay_client,
        project_financing_repository=project_financing_repository,
        financier_access_policy=financier_access_policy,
        create_project_financing_use_case=CreateProjectFinancingUseCase(
            user_repository,
            project_repository,
            project_financing_repository,
            cost_item_repository,
            financier_access_policy,
            financing_activity_repository,
        ),
        decide_project_financing_use_case=DecideProjectFinancingUseCase(
            user_repository,
            project_repository,
            project_financing_repository,
            cost_item_repository,
            financier_access_policy,
            financing_activity_repository,
        ),
        list_financier_pending_approvals_use_case=ListFinancierPendingApprovalsUseCase(
            user_repository,
            project_repository,
            project_financing_repository,
            financier_access_policy,
        ),
        list_project_financings_use_case=ListProjectFinancingsUseCase(
            user_repository,
            project_repository,
            project_financing_repository,
            financier_access_policy,
        ),
        list_financier_portfolio_use_case=ListFinancierPortfolioUseCase(financier_portfolio_loader),
        get_financier_monitoring_use_case=GetFinancierMonitoringUseCase(
            get_financier_project_detail_use_case
        ),
        get_financier_dashboard_use_case=get_financier_dashboard_use_case,
        list_financier_alerts_use_case=ListFinancierAlertsUseCase(financier_portfolio_loader),
        list_financier_disbursements_use_case=ListFinancierDisbursementsUseCase(
            financier_portfolio_loader,
            financing_disbursement_repository,
            project_repository,
            project_financing_repository,
        ),
        list_financier_documents_use_case=ListFinancierDocumentsUseCase(
            financier_portfolio_loader,
            financing_document_repository,
            project_repository,
        ),
        list_financier_activity_use_case=ListFinancierActivityUseCase(
            financier_portfolio_loader,
            financing_activity_repository,
        ),
        create_financing_disbursement_use_case=CreateFinancingDisbursementUseCase(
            user_repository,
            project_repository,
            project_financing_repository,
            financing_disbursement_repository,
            financing_activity_repository,
            financier_access_policy,
        ),
        update_financing_disbursement_use_case=UpdateFinancingDisbursementUseCase(
            user_repository,
            project_repository,
            project_financing_repository,
            financing_disbursement_repository,
            financing_activity_repository,
            financier_access_policy,
        ),
        create_financing_document_use_case=CreateFinancingDocumentUseCase(
            user_repository,
            project_repository,
            project_financing_repository,
            financing_document_repository,
            financing_activity_repository,
            financier_access_policy,
        ),
        validate_financing_document_use_case=ValidateFinancingDocumentUseCase(
            user_repository,
            project_repository,
            project_financing_repository,
            financing_document_repository,
            financing_activity_repository,
            financier_access_policy,
        ),
        export_financier_portfolio_report_use_case=ExportFinancierPortfolioReportUseCase(
            get_financier_dashboard_use_case
        ),
        get_project_billing_integration_use_case=GetProjectBillingIntegrationUseCase(
            user_repository,
            project_repository,
            billing_integration_repository,
            project_access_policy,
        ),
        configure_project_billing_integration_use_case=ConfigureProjectBillingIntegrationUseCase(
            user_repository,
            project_repository,
            billing_integration_repository,
            project_access_policy,
            hash_service,
        ),
        regenerate_project_billing_api_key_use_case=RegenerateProjectBillingApiKeyUseCase(
            user_repository,
            project_repository,
            billing_integration_repository,
            project_access_policy,
            hash_service,
        ),
        sync_billing_via_api_key_use_case=SyncBillingViaApiKeyUseCase(
            project_repository,
            billing_integration_repository,
            hash_service,
            analysis_repository,
        ),
        export_financier_credit_report_use_case=ExportFinancierCreditReportUseCase(
            financier_portfolio_loader,
            billing_integration_repository,
            analysis_repository,
        ),
        sync_project_billing_integration_use_case=SyncProjectBillingIntegrationUseCase(
            user_repository,
            project_repository,
            billing_integration_repository,
            project_access_policy,
            analysis_repository,
        ),
        list_financier_billing_integrations_use_case=ListFinancierBillingIntegrationsUseCase(
            financier_portfolio_loader,
            billing_integration_repository,
        ),
    )

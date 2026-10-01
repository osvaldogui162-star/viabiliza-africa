from flask import Flask, jsonify

from app.config import Config
from app.di.container import Container, build_container
from app.extensions import cors
from app.presentation.api.error_handlers import register_error_handlers
from app.presentation.api.v1.admin_routes import admin_bp
from app.presentation.api.v1.auth_routes import auth_bp
from app.presentation.api.v1.analysis_routes import analysis_bp
from app.presentation.api.v1.automation_routes import automation_bp
from app.presentation.api.v1.collaboration_routes import collaboration_bp
from app.presentation.api.v1.ingestion_routes import ingestion_bp
from app.presentation.api.v1.project_routes import projects_bp
from app.presentation.api.v1.report_routes import reports_bp
from app.presentation.api.v1.subscription_routes import subscriptions_bp
from app.presentation.api.v1.verify_routes import verify_bp
from app.presentation.api.v1.notification_routes import notifications_bp
from app.presentation.api.v1.financier_routes import financier_bp
from app.presentation.api.v1.terminal_routes import terminal_bp
from app.presentation.api.v1.office_routes import office_bp
from app.presentation.api.v1.erp_billing_routes import erp_billing_bp
from app.presentation.middleware.auth_middleware import register_auth_middleware


def create_app(config: Config | None = None) -> Flask:
    """Application Factory Pattern."""
    app = Flask(__name__)
    cfg = config or Config()
    app.config["SECRET_KEY"] = cfg.SECRET_KEY
    app.config["DEBUG"] = cfg.DEBUG

    container: Container = build_container(cfg)
    app.extensions["container"] = container

    # CORS global: cobre todas as rotas da API (incluindo /api/v1/*).
    cors.init_app(
        app,
        origins=cfg.CORS_ORIGINS,
        supports_credentials=True,
        methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Terminal-Api-Key"],
        expose_headers=["Content-Disposition"],
        intercept_exceptions=True,
    )

    auth_bp.container = container  # type: ignore[attr-defined]
    admin_bp.container = container  # type: ignore[attr-defined]
    projects_bp.container = container  # type: ignore[attr-defined]
    automation_bp.container = container  # type: ignore[attr-defined]
    ingestion_bp.container = container  # type: ignore[attr-defined]
    analysis_bp.container = container  # type: ignore[attr-defined]
    collaboration_bp.container = container  # type: ignore[attr-defined]
    reports_bp.container = container  # type: ignore[attr-defined]
    verify_bp.container = container  # type: ignore[attr-defined]
    notifications_bp.container = container  # type: ignore[attr-defined]
    subscriptions_bp.container = container  # type: ignore[attr-defined]
    financier_bp.container = container  # type: ignore[attr-defined]
    terminal_bp.container = container  # type: ignore[attr-defined]
    office_bp.container = container  # type: ignore[attr-defined]
    erp_billing_bp.container = container  # type: ignore[attr-defined]
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(automation_bp)
    app.register_blueprint(ingestion_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(collaboration_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(verify_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(subscriptions_bp)
    app.register_blueprint(financier_bp)
    app.register_blueprint(terminal_bp)
    app.register_blueprint(office_bp)
    app.register_blueprint(erp_billing_bp)

    register_error_handlers(app)
    register_auth_middleware(app, container.token_service, container.user_repository)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "viabiliza-africa-api"}), 200

    return app

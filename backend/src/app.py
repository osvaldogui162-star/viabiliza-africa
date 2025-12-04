"""
Viabiliza+África - Backend API
Sistema de gestão de planos estratégicos, financeiros e de negócio
"""

from flask import Flask
from flask_cors import CORS
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.settings import config
from backend.src import db
from backend.src.routes import spreadsheet_routes, health_routes, frontend_routes, project_routes, equipment_routes, import_routes
from backend.src.models.project import Project
from backend.src.models.equipment import Equipment


def create_app(config_name=None):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    # Create data directory if it doesn't exist
    data_dir = Path(app.config.get('DATA_DIR', 'data'))
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Warning: Could not create database tables: {e}")
            print("This might be normal if tables already exist.")
    
    # Enable CORS - allow all origins in development
    if app.config['FLASK_ENV'] == 'development':
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    else:
        CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    app.register_blueprint(spreadsheet_routes.bp)
    app.register_blueprint(health_routes.bp)
    app.register_blueprint(frontend_routes.bp)
    app.register_blueprint(project_routes.bp)
    app.register_blueprint(equipment_routes.bp)
    app.register_blueprint(import_routes.bp)
    
    return app


def open_browser(url, delay=1.5):
    """
    Open browser after a delay
    
    Args:
        url: URL to open
        delay: Delay in seconds before opening
    """
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"\n🌐 Navegador aberto automaticamente: {url}")
        except Exception as e:
            print(f"\n⚠️  Não foi possível abrir o navegador automaticamente: {e}")
            print(f"   Por favor, abra manualmente: {url}")
    
    thread = threading.Thread(target=_open)
    thread.daemon = True
    thread.start()


def main():
    """Main entry point"""
    app = create_app()
    
    host = app.config['FLASK_HOST']
    port = app.config['FLASK_PORT']
    url = f"http://localhost:{port}"
    
    print("=" * 60)
    print("Starting Viabiliza+África Backend API...")
    print("=" * 60)
    print(f"Environment: {app.config['FLASK_ENV']}")
    print(f"Frontend: {url}")
    print(f"API: {url}/api")
    print("\nEndpoints:")
    print("  GET  /                    → Frontend (index.html)")
    print("  GET  /api/spreadsheet/<sheet_name>")
    print("  POST /api/spreadsheet/update")
    print("  POST /api/spreadsheet/<sheet_name>/calculate")
    print("  POST /api/spreadsheet/<sheet_name>/save")
    print("  POST /api/spreadsheet/pressupostos/calculate-rst")
    print("  GET  /api/projects              → List projects")
    print("  POST /api/projects              → Create project")
    print("  GET  /api/projects/<id>         → Get project")
    print("  PUT  /api/projects/<id>         → Update project")
    print("  DELETE /api/projects/<id>        → Delete project")
    print("  GET  /api/projects/current      → Get current project")
    print("  POST /api/projects/current      → Set current project")
    print("  GET  /api/equipment/<project_id>/<sheet_key> → List equipment")
    print("  POST /api/equipment              → Create equipment")
    print("  GET  /api/equipment/<id>         → Get equipment")
    print("  PUT  /api/equipment/<id>         → Update equipment")
    print("  DELETE /api/equipment/<id>        → Delete equipment")
    print("  POST /api/equipment/<project_id>/<sheet_key>/bulk → Save bulk equipment")
    print("  POST /api/import/excel              → Import data from Excel")
    print("  GET  /api/import/template           → Download Excel template")
    print("  GET  /api/health")
    print("=" * 60)
    
    # Open browser automatically
    if app.config['FLASK_ENV'] == 'development':
        open_browser(url)
    
    app.run(
        debug=app.config['FLASK_DEBUG'],
        host=host,
        port=port
    )


if __name__ == '__main__':
    main()


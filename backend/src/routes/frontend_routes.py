"""
Frontend routes - Serve static files
"""

from flask import Blueprint, send_from_directory
from pathlib import Path
import os

bp = Blueprint('frontend', __name__)

# Get frontend directory path
FRONTEND_DIR = Path(__file__).parent.parent.parent.parent / 'frontend'


@bp.route('/')
def index():
    """Serve index.html"""
    return send_from_directory(str(FRONTEND_DIR), 'index.html')


@bp.route('/<path:path>')
def serve_static(path):
    """Serve static files from frontend directory"""
    # Security: prevent directory traversal
    if '..' in path or path.startswith('/'):
        return "Forbidden", 403
    
    # Try to serve the file
    file_path = FRONTEND_DIR / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(str(FRONTEND_DIR), path)
    
    # If file doesn't exist, serve index.html (for SPA routing)
    return send_from_directory(str(FRONTEND_DIR), 'index.html')


"""
Health check routes
"""

from flask import Blueprint, jsonify
from datetime import datetime

bp = Blueprint('health', __name__, url_prefix='/api')


@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Viabiliza+África API',
        'version': '1.0.0'
    })


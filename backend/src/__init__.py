"""
Backend source package initialization
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import models after db initialization
from backend.src.models import project, storage, equipment

__all__ = ['db', 'project', 'storage', 'equipment']

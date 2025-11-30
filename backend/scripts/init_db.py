"""
Initialize database
Creates database tables if they don't exist
"""

import sys
from pathlib import Path
from sqlalchemy import inspect

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.src.app import create_app
from backend.src import db
from backend.src.models.project import Project

def init_database():
    """Initialize database and create tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Get table names using inspect (compatible with newer SQLAlchemy versions)
        try:
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
        except Exception as e:
            table_names = ["N/A - Could not list tables"]
            print(f"Warning: Could not list tables: {e}")
        
        print("=" * 60)
        print("Database initialized successfully!")
        print("=" * 60)
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Tables created: {', '.join(table_names) if table_names else 'N/A'}")
        print("=" * 60)

if __name__ == '__main__':
    init_database()


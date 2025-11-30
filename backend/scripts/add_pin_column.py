"""
Script para adicionar a coluna PIN à tabela projects
Execute este script se o banco de dados já existir e não tiver a coluna PIN
"""

import sys
from pathlib import Path
from sqlalchemy import inspect

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.src.app import create_app
from backend.src import db
from backend.src.models.project import Project

def add_pin_column():
    """Add PIN column to projects table if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column exists using inspector
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('projects')]
            
            if 'pin' in columns:
                print("✓ Coluna PIN já existe na tabela projects")
                return
            
            # Column doesn't exist, add it
            print("Adicionando coluna PIN à tabela projects...")
            
            # Get database type
            db_uri = app.config['SQLALCHEMY_DATABASE_URI'].lower()
            
            # For SQLite
            if 'sqlite' in db_uri:
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN pin VARCHAR(4)"))
            # For PostgreSQL
            elif 'postgresql' in db_uri:
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN pin VARCHAR(4)"))
            # For MySQL
            elif 'mysql' in db_uri:
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN pin VARCHAR(4)"))
            else:
                # Try generic SQL
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN pin VARCHAR(4)"))
            
            db.session.commit()
            print("✓ Coluna PIN adicionada com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            import traceback
            error_trace = traceback.format_exc()
            print(f"⚠️  Erro ao adicionar coluna PIN: {e}")
            print(f"   Detalhes: {error_trace}")
            print("   Isso pode ser normal se a coluna já existir ou se houver outro problema.")
            print("   Tente recriar o banco de dados executando: python backend/scripts/init_db.py")

if __name__ == '__main__':
    add_pin_column()


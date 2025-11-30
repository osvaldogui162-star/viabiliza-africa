"""
Project model for database
"""

from datetime import datetime
from backend.src import db


class Project(db.Model):
    """
    Project model
    """
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    primeiro_ano = db.Column(db.Integer, nullable=False)
    num_anos = db.Column(db.Integer, nullable=False)
    unidade_monetaria = db.Column(db.String(10), nullable=False, default='EUR')
    pin = db.Column(db.String(4), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """
        Convert project to dictionary
        
        Returns:
            Dictionary representation of the project
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'primeiroAno': self.primeiro_ano,
            'numAnos': self.num_anos,
            'unidadeMonetaria': self.unidade_monetaria,
            'hasPin': bool(self.pin),  # Indica se o projeto tem PIN, mas não expõe o valor
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create project from dictionary
        
        Args:
            data: Dictionary with project data
            
        Returns:
            Project instance
        """
        return cls(
            nome=data.get('nome'),
            primeiro_ano=data.get('primeiroAno') or data.get('primeiro_ano'),
            num_anos=data.get('numAnos') or data.get('num_anos'),
            unidade_monetaria=data.get('unidadeMonetaria') or data.get('unidade_monetaria', 'EUR'),
            pin=data.get('pin') if data.get('pin') else None
        )
    
    def __repr__(self):
        return f'<Project {self.nome}>'


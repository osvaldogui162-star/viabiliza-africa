"""
Equipment model for database
"""

from datetime import datetime
from backend.src import db


class Equipment(db.Model):
    """
    Equipment model - stores equipment data for investment sheets
    """
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sheet_key = db.Column(db.String(100), nullable=False)  # e.g., 'ativos-tangiveis-equipamento-basico'
    equipment_name = db.Column(db.String(255), nullable=False)
    ano0 = db.Column(db.String(50), default='0,00')
    year_values = db.Column(db.Text)  # JSON string with year values: {"2023": "1000,00", "2024": "2000,00", ...}
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    project = db.relationship('Project', backref='equipment')
    
    def to_dict(self):
        """
        Convert equipment to dictionary
        
        Returns:
            Dictionary representation of the equipment
        """
        import json
        year_values = {}
        if self.year_values:
            try:
                year_values = json.loads(self.year_values)
            except:
                pass
        
        return {
            'id': self.id,
            'projectId': self.project_id,
            'sheetKey': self.sheet_key,
            'equipmentName': self.equipment_name,
            'ano0': self.ano0,
            'yearValues': year_values,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data, project_id):
        """
        Create equipment from dictionary
        
        Args:
            data: Dictionary with equipment data
            project_id: Project ID
            
        Returns:
            Equipment instance
        """
        import json
        year_values = data.get('yearValues', {})
        if isinstance(year_values, dict):
            year_values = json.dumps(year_values)
        
        return cls(
            project_id=project_id,
            sheet_key=data.get('sheetKey'),
            equipment_name=data.get('equipmentName'),
            ano0=data.get('ano0', '0,00'),
            year_values=year_values
        )
    
    def __repr__(self):
        return f'<Equipment {self.equipment_name}>'


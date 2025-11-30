"""
Equipment routes
Handle equipment CRUD operations
"""

from flask import Blueprint, request, jsonify
from backend.src import db
from backend.src.models.equipment import Equipment
from backend.src.models.project import Project
from datetime import datetime
import json

bp = Blueprint('equipment', __name__, url_prefix='/api/equipment')


@bp.route('/<int:project_id>/<sheet_key>', methods=['GET'])
def list_equipment(project_id, sheet_key):
    """
    List all equipment for a specific project and sheet
    
    Args:
        project_id: Project ID
        sheet_key: Sheet key (e.g., 'ativos-tangiveis-equipamento-basico')
    
    Returns:
        JSON array of equipment
    """
    try:
        # Verify project exists
        project = Project.query.get_or_404(project_id)
        
        equipment_list = Equipment.query.filter_by(
            project_id=project_id,
            sheet_key=sheet_key
        ).order_by(Equipment.created_at.asc()).all()
        
        return jsonify({
            'success': True,
            'equipment': [eq.to_dict() for eq in equipment_list]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('', methods=['POST'])
def create_equipment():
    """
    Create a new equipment
    
    Request body:
        {
            "projectId": 1,
            "sheetKey": "ativos-tangiveis-equipamento-basico",
            "equipmentName": "Máquina A",
            "ano0": "1000,00",
            "yearValues": {"2023": "2000,00", "2024": "3000,00"}
        }
    
    Returns:
        JSON with created equipment
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['projectId', 'sheetKey', 'equipmentName']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório ausente: {field}'
                }), 400
        
        # Verify project exists
        project = Project.query.get_or_404(data['projectId'])
        
        # Create equipment
        equipment = Equipment.from_dict(data, data['projectId'])
        db.session.add(equipment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'equipment': equipment.to_dict(),
            'message': f'Equipamento "{equipment.equipment_name}" criado com sucesso!'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error creating equipment: {error_trace}")
        return jsonify({
            'success': False,
            'error': f'Erro ao criar equipamento: {str(e)}'
        }), 500


@bp.route('/<int:equipment_id>', methods=['GET'])
def get_equipment(equipment_id):
    """
    Get a specific equipment by ID
    
    Args:
        equipment_id: Equipment ID
    
    Returns:
        JSON with equipment data
    """
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        return jsonify({
            'success': True,
            'equipment': equipment.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404


@bp.route('/<int:equipment_id>', methods=['PUT'])
def update_equipment(equipment_id):
    """
    Update an equipment
    
    Args:
        equipment_id: Equipment ID
    
    Request body:
        {
            "equipmentName": "Máquina A Atualizada",
            "ano0": "1500,00",
            "yearValues": {"2023": "2500,00", "2024": "3500,00"}
        }
    
    Returns:
        JSON with updated equipment
    """
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'equipmentName' in data:
            equipment.equipment_name = data['equipmentName']
        
        if 'ano0' in data:
            equipment.ano0 = data['ano0']
        
        if 'yearValues' in data:
            if isinstance(data['yearValues'], dict):
                equipment.year_values = json.dumps(data['yearValues'])
            else:
                equipment.year_values = data['yearValues']
        
        equipment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'equipment': equipment.to_dict(),
            'message': f'Equipamento "{equipment.equipment_name}" atualizado com sucesso!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao atualizar equipamento: {str(e)}'
        }), 500


@bp.route('/<int:equipment_id>', methods=['DELETE'])
def delete_equipment(equipment_id):
    """
    Delete an equipment
    
    Args:
        equipment_id: Equipment ID
    
    Returns:
        JSON confirmation
    """
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        equipment_name = equipment.equipment_name
        db.session.delete(equipment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipamento "{equipment_name}" deletado com sucesso!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao deletar equipamento: {str(e)}'
        }), 500


@bp.route('/<int:project_id>/<sheet_key>/bulk', methods=['POST'])
def save_bulk_equipment(project_id, sheet_key):
    """
    Save all equipment for a sheet in bulk (replace all)
    
    Request body:
        {
            "equipment": [
                {
                    "equipmentName": "Máquina A",
                    "ano0": "1000,00",
                    "yearValues": {"2023": "2000,00"}
                },
                ...
            ]
        }
    
    Returns:
        JSON with saved equipment list
    """
    try:
        # Verify project exists
        project = Project.query.get_or_404(project_id)
        
        data = request.get_json()
        equipment_list = data.get('equipment', [])
        
        # Delete existing equipment for this sheet
        Equipment.query.filter_by(
            project_id=project_id,
            sheet_key=sheet_key
        ).delete()
        
        # Create new equipment
        saved_equipment = []
        for eq_data in equipment_list:
            eq_data['projectId'] = project_id
            eq_data['sheetKey'] = sheet_key
            equipment = Equipment.from_dict(eq_data, project_id)
            db.session.add(equipment)
            saved_equipment.append(equipment)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'equipment': [eq.to_dict() for eq in saved_equipment],
            'message': f'{len(saved_equipment)} equipamento(s) salvo(s) com sucesso!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error saving bulk equipment: {error_trace}")
        return jsonify({
            'success': False,
            'error': f'Erro ao salvar equipamentos: {str(e)}'
        }), 500


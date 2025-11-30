"""
Project routes
Handle project CRUD operations
"""

from flask import Blueprint, request, jsonify
from backend.src import db
from backend.src.models.project import Project
from datetime import datetime

bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@bp.route('', methods=['GET'])
def list_projects():
    """
    List all projects
    
    Returns:
        JSON array of projects
    """
    try:
        projects = Project.query.order_by(Project.created_at.desc()).all()
        projects_list = []
        for project in projects:
            try:
                projects_list.append(project.to_dict())
            except Exception as e:
                # Log error but continue with other projects
                print(f"Error serializing project {project.id}: {e}")
                # Try to create a basic dict without PIN
                projects_list.append({
                    'id': project.id,
                    'nome': project.nome,
                    'primeiroAno': project.primeiro_ano,
                    'numAnos': project.num_anos,
                    'unidadeMonetaria': project.unidade_monetaria,
                    'hasPin': bool(project.pin),
                    'createdAt': project.created_at.isoformat() if project.created_at else None,
                    'updatedAt': project.updated_at.isoformat() if project.updated_at else None
                })
        return jsonify({
            'success': True,
            'projects': projects_list
        }), 200
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error listing projects: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('', methods=['POST'])
def create_project():
    """
    Create a new project
    
    Request body:
        {
            "nome": "Nome do Projeto",
            "primeiroAno": 2022,
            "numAnos": 5,
            "unidadeMonetaria": "EUR",
            "pin": "1234"
        }
    
    Returns:
        JSON with created project
    """
    try:
        data = request.get_json()
        
        # Debug: log received data
        print(f"Received data: {data}")
        
        # Check if data is None
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos. Por favor, envie um JSON válido.'
            }), 400
        
        # Validate required fields
        required_fields = ['nome', 'primeiroAno', 'numAnos', 'unidadeMonetaria', 'pin']
        missing_fields = [field for field in required_fields if field not in data or (field == 'pin' and not data.get('pin'))]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
            }), 400
        
        # Validate PIN: must be exactly 4 digits
        pin = str(data['pin']).strip()
        if not pin.isdigit() or len(pin) != 4:
            return jsonify({
                'success': False,
                'error': 'PIN deve conter exatamente 4 dígitos numéricos'
            }), 400
        
        # Validate data types and ranges
        if not isinstance(data['primeiroAno'], int) or data['primeiroAno'] < 2000 or data['primeiroAno'] > 2100:
            return jsonify({
                'success': False,
                'error': 'primeiroAno deve ser um número entre 2000 e 2100'
            }), 400
        
        if not isinstance(data['numAnos'], int) or data['numAnos'] < 1 or data['numAnos'] > 20:
            return jsonify({
                'success': False,
                'error': 'numAnos deve ser um número entre 1 e 20'
            }), 400
        
        # Check if project name already exists
        existing = Project.query.filter_by(nome=data['nome']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Já existe um projeto com este nome'
            }), 400
        
        # Create new project
        project = Project.from_dict(data)
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': f'Projeto "{project.nome}" criado com sucesso!'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error creating project: {error_trace}")
        return jsonify({
            'success': False,
            'error': f'Erro ao criar projeto: {str(e)}'
        }), 500


@bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Get a specific project by ID
    
    Args:
        project_id: Project ID
    
    Returns:
        JSON with project data
    """
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify({
            'success': True,
            'project': project.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404


@bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """
    Update a project
    
    Args:
        project_id: Project ID
    
    Request body:
        {
            "nome": "Nome Atualizado",
            "primeiroAno": 2023,
            "numAnos": 6,
            "unidadeMonetaria": "USD"
        }
    
    Returns:
        JSON with updated project
    """
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'nome' in data:
            # Check if new name conflicts with existing project
            existing = Project.query.filter_by(nome=data['nome']).first()
            if existing and existing.id != project_id:
                return jsonify({
                    'success': False,
                    'error': 'Já existe um projeto com este nome'
                }), 400
            project.nome = data['nome']
        
        if 'primeiroAno' in data:
            if not isinstance(data['primeiroAno'], int) or data['primeiroAno'] < 2000 or data['primeiroAno'] > 2100:
                return jsonify({
                    'success': False,
                    'error': 'primeiroAno deve ser um número entre 2000 e 2100'
                }), 400
            project.primeiro_ano = data['primeiroAno']
        
        if 'numAnos' in data:
            if not isinstance(data['numAnos'], int) or data['numAnos'] < 1 or data['numAnos'] > 20:
                return jsonify({
                    'success': False,
                    'error': 'numAnos deve ser um número entre 1 e 20'
                }), 400
            project.num_anos = data['numAnos']
        
        if 'unidadeMonetaria' in data:
            project.unidade_monetaria = data['unidadeMonetaria']
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': f'Projeto "{project.nome}" atualizado com sucesso!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    Delete a project
    
    Args:
        project_id: Project ID
    
    Returns:
        JSON confirmation
    """
    try:
        project = Project.query.get_or_404(project_id)
        project_name = project.nome
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Projeto "{project_name}" deletado com sucesso!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/current', methods=['GET'])
def get_current_project():
    """
    Get the current active project (most recently created or updated)
    
    Returns:
        JSON with current project
    """
    try:
        project = Project.query.order_by(Project.updated_at.desc()).first()
        if project:
            try:
                return jsonify({
                    'success': True,
                    'project': project.to_dict()
                }), 200
            except Exception as e:
                # If to_dict fails, create basic dict
                import traceback
                print(f"Error in to_dict for project {project.id}: {traceback.format_exc()}")
                return jsonify({
                    'success': True,
                    'project': {
                        'id': project.id,
                        'nome': project.nome,
                        'primeiroAno': project.primeiro_ano,
                        'numAnos': project.num_anos,
                        'unidadeMonetaria': project.unidade_monetaria,
                        'hasPin': bool(project.pin),
                        'createdAt': project.created_at.isoformat() if project.created_at else None,
                        'updatedAt': project.updated_at.isoformat() if project.updated_at else None
                    }
                }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Nenhum projeto encontrado'
            }), 404
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error getting current project: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/current', methods=['POST'])
def set_current_project():
    """
    Set a project as current (update its updated_at timestamp)
    
    Request body:
        {
            "projectId": 1
        }
    
    Returns:
        JSON with current project
    """
    try:
        data = request.get_json()
        project_id = data.get('projectId')
        
        if not project_id:
            return jsonify({
                'success': False,
                'error': 'projectId é obrigatório'
            }), 400
        
        project = Project.query.get_or_404(project_id)
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': f'Projeto "{project.nome}" definido como atual'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/<int:project_id>/verify-pin', methods=['POST'])
def verify_pin(project_id):
    """
    Verify PIN for a project
    
    Args:
        project_id: Project ID
    
    Request body:
        {
            "pin": "1234"
        }
    
    Returns:
        JSON with verification result
    """
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        if not data or 'pin' not in data:
            return jsonify({
                'success': False,
                'error': 'PIN não fornecido'
            }), 400
        
        provided_pin = str(data['pin']).strip()
        
        # Check if project has a PIN
        if not project.pin:
            return jsonify({
                'success': False,
                'error': 'Este projeto não possui PIN configurado'
            }), 400
        
        # Verify PIN
        if provided_pin == project.pin:
            return jsonify({
                'success': True,
                'message': 'PIN correto',
                'project': project.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'PIN incorreto'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


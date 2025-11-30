"""
Spreadsheet API routes
"""

from flask import Blueprint, request, jsonify
from ..models.storage import DataStorage
from ..services.calculations import recalculate_formulas, calculate_rst
from ..utils.parsers import parse_value, format_decimal

bp = Blueprint('spreadsheet', __name__, url_prefix='/api/spreadsheet')
storage = DataStorage()


@bp.route('/<sheet_name>', methods=['GET'])
def get_spreadsheet(sheet_name: str):
    """Get spreadsheet data"""
    data = storage.load_sheet_data(sheet_name)
    
    if not data:
        # Return default structure
        return jsonify({
            'title': 'Plano Financeiro',
            'subtitle': f'{sheet_name}',
            'headers': ['Parâmetro', 'Inicial', 'Ano 1', 'Ano 2', 'Ano 3', 'Ano 4', 'Ano 5'],
            'rows': []
        })
    
    return jsonify(data)


@bp.route('/update', methods=['POST'])
def update_spreadsheet():
    """Update a cell in the spreadsheet"""
    try:
        data = request.json
        sheet_name = data.get('sheet', 'pressupostos')
        row_name = data.get('row_name')
        column_index = data.get('column_index')
        value = data.get('value')
        
        if not all([row_name, column_index is not None, value is not None]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Load current sheet data
        sheet_data = storage.load_sheet_data(sheet_name)
        
        if 'rows' not in sheet_data:
            sheet_data['rows'] = []
        
        # Find the row
        row_found = False
        for row in sheet_data['rows']:
            if row and len(row) > 0 and row[0] == row_name:
                # Ensure row has enough columns
                while len(row) <= column_index:
                    row.append('')
                row[column_index] = value
                row_found = True
                break
        
        if not row_found:
            # Create new row
            new_row = [row_name] + [''] * (column_index)
            new_row.append(value)
            sheet_data['rows'].append(new_row)
        
        # Recalculate formulas
        calculated_values = recalculate_formulas(sheet_data, sheet_name)
        
        # Save updated data
        storage.save_sheet_data(sheet_name, sheet_data)
        
        return jsonify({
            'success': True,
            'calculated_values': calculated_values
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<sheet_name>/calculate', methods=['POST'])
def calculate_spreadsheet(sheet_name: str):
    """Recalculate all formulas in a spreadsheet"""
    try:
        sheet_data = storage.load_sheet_data(sheet_name)
        calculated_values = recalculate_formulas(sheet_data, sheet_name)
        
        return jsonify({
            'success': True,
            'calculated_values': calculated_values
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<sheet_name>/save', methods=['POST'])
def save_spreadsheet(sheet_name: str):
    """Save entire spreadsheet"""
    try:
        data = request.json
        storage.save_sheet_data(sheet_name, data)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/pressupostos/calculate-rst', methods=['POST'])
def calculate_rst_endpoint():
    """Calculate Reserva de Segurança de Tesouraria (RST) based on rendimentos"""
    try:
        data = request.json
        rendimentos_data = data.get('rendimentos', {})
        
        # Extract rendimentos values
        rendimentos = {}
        if isinstance(rendimentos_data, dict):
            if 'rows' in rendimentos_data:
                # Find rendimentos row
                for row in rendimentos_data['rows']:
                    if row and len(row) > 0:
                        row_name = row[0]
                        if 'Rendimentos' in row_name or 'Vendas' in row_name:
                            # Sum all revenue sources for each year
                            for col_idx in range(1, min(7, len(row))):
                                year_key = f'Ano {col_idx}'
                                if year_key not in rendimentos:
                                    rendimentos[year_key] = 0
                                rendimentos[year_key] += parse_value(row[col_idx])
        
        # Calculate RST
        rst_values = calculate_rst(rendimentos)
        
        # Format values
        formatted_rst = {}
        for year, value in rst_values.items():
            formatted_rst[year] = format_decimal(value, 1)
        
        return jsonify({
            'success': True,
            'rst_values': formatted_rst
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


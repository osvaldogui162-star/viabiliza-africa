"""
Import routes
Handle bulk import of data from Excel files
"""

import pandas as pd
import io
from flask import Blueprint, request, jsonify
from backend.src import db
from backend.src.models.equipment import Equipment
from backend.src.models.project import Project

bp = Blueprint('import', __name__, url_prefix='/api/import')

def normalize_column_names(df):
    """
    Normalize column names to standard keys
    """
    column_map = {
        'descrição': 'description',
        'descricao': 'description',
        'item': 'description',
        'produto': 'description',
        'designação': 'description',
        'quantidade': 'quantity',
        'qtd': 'quantity',
        'unidades': 'quantity',
        'preço unitário': 'unit_price',
        'preco unitario': 'unit_price',
        'preço': 'unit_price',
        'valor': 'unit_price',
        'custo': 'unit_price',
        'valor unitário': 'unit_price',
        'total': 'total',
        'valor total': 'total',
        'categoria': 'category',
        'tipo': 'category',
        'vida útil': 'lifespan',
        'vida util': 'lifespan',
        'anos': 'lifespan'
    }
    
    # Normalize to lowercase and strip
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    # Rename columns based on map
    new_columns = {}
    for col in df.columns:
        for key, value in column_map.items():
            if key in col:
                new_columns[col] = value
                break
    
    return df.rename(columns=new_columns)

@bp.route('/excel', methods=['POST'])
def import_excel():
    """
    Import data from Excel file
    
    Request:
        File: 'file' (xlsx)
        Form data: 'project_id', 'sheet_key' (optional)
        
    Returns:
        JSON with parsed data
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nome do arquivo vazio'
            }), 400
            
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'Formato inválido. Use arquivos Excel (.xlsx, .xls)'
            }), 400
            
        # Read Excel file
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro ao ler arquivo Excel: {str(e)}'
            }), 400
            
        # Check if empty
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'O arquivo está vazio'
            }), 400
            
        # Normalize columns
        df = normalize_column_names(df)
        
        # Validate required columns
        required_cols = ['description'] # Minimal requirement
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            # If description is missing, maybe use the first column?
            # Let's try to be flexible
            if len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: 'description'})
            else:
                return jsonify({
                    'success': False,
                    'error': 'Não foi possível identificar a coluna de descrição/item'
                }), 400
        
        # Ensure other columns exist with defaults
        if 'quantity' not in df.columns:
            df['quantity'] = 1
            
        if 'unit_price' not in df.columns:
            if 'total' in df.columns:
                # Try to calc unit price from total / quantity
                df['unit_price'] = pd.to_numeric(df['total'], errors='coerce') / pd.to_numeric(df['quantity'], errors='coerce')
            else:
                df['unit_price'] = 0
                
        # Fill NaN values
        df['description'] = df['description'].fillna('Item sem nome')
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1)
        df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0)
        
        # Calculate total if not present
        if 'total' not in df.columns:
            df['total'] = df['quantity'] * df['unit_price']
            
        # Convert to list of dicts
        items = []
        for _, row in df.iterrows():
            items.append({
                'description': str(row['description']),
                'quantity': float(row['quantity']),
                'unit_price': float(row['unit_price']),
                'total': float(row['quantity'] * row['unit_price']),
                'category': str(row['category']) if 'category' in df.columns and not pd.isna(row['category']) else 'Geral'
            })
        
        # Save to database if project_id and sheet_key are provided
        project_id = request.form.get('project_id')
        sheet_key = request.form.get('sheet_key', 'imported_items')
        
        if project_id:
            try:
                project_id = int(project_id)
                project = Project.query.get(project_id)
                
                if not project:
                    return jsonify({
                        'success': False,
                        'error': f'Projeto com ID {project_id} não encontrado'
                    }), 404
                
                # Save items as equipment entries
                saved_count = 0
                for item in items:
                    try:
                        # Determine lifespan based on category
                        lifespan = 10  # Default
                        category_lower = item['category'].lower()
                        if 'informatic' in category_lower or 'computador' in category_lower:
                            lifespan = 4
                        elif 'mobiliari' in category_lower or 'mesa' in category_lower or 'cadeira' in category_lower:
                            lifespan = 10
                        elif 'veiculo' in category_lower or 'viatura' in category_lower:
                            lifespan = 4
                        elif 'maquinaria' in category_lower or 'equipamento' in category_lower:
                            lifespan = 8
                        
                        # Format value with AOA currency format (Angola uses comma as decimal separator)
                        # Convert to string with proper formatting
                        total_value = item['total']
                        # Format: 1.234.567,89 (Angola format) - comma for decimal, dot for thousands
                        if total_value >= 1000:
                            # Format with thousands separator
                            formatted_value = f"{total_value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                        else:
                            # No thousands separator needed
                            formatted_value = f"{total_value:.2f}".replace('.', ',')
                        
                        # Create equipment entry
                        equipment = Equipment(
                            project_id=project_id,
                            sheet_key=sheet_key,
                            equipment_name=item['description'],
                            ano0=formatted_value,
                            year_values='{}'
                        )
                        db.session.add(equipment)
                        saved_count += 1
                    except Exception as e:
                        print(f"Erro ao salvar item {item['description']}: {e}")
                        continue
                
                db.session.commit()
                
                # Get sheet display name for better feedback
                sheet_display_names = {
                    'ativos-tangiveis-terrenos': 'Terrenos e Recursos Naturais',
                    'ativos-tangiveis-edificios': 'Edifícios e Outras Construções',
                    'ativos-tangiveis-equipamento-basico': 'Equipamento Básico',
                    'ativos-tangiveis-equipamento-transporte': 'Equipamento de Transporte',
                    'ativos-tangiveis-equipamento-administrativo': 'Equipamento Administrativo',
                    'ativos-tangiveis-equipamentos-biologicos': 'Equipamentos Biológicos',
                    'ativos-intangiveis-goodwill': 'Goodwill',
                    'ativos-intangiveis-projetos-desenvolvimento': 'Projetos de Desenvolvimento',
                    'ativos-intangiveis-programas-computador': 'Programas de Computador',
                    'ativos-intangiveis-propriedade-industrial': 'Propriedade Industrial',
                    'ativos-intangiveis-outros': 'Outros Ativos Intangíveis'
                }
                sheet_name = sheet_display_names.get(sheet_key, sheet_key)
                
                # Calculate total value
                total_value = sum(item['total'] for item in items)
                # Format with AOA format (comma as decimal separator)
                if total_value >= 1000:
                    total_formatted = f"{total_value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                else:
                    total_formatted = f"{total_value:.2f}".replace('.', ',')
                
                return jsonify({
                    'success': True,
                    'count': len(items),
                    'saved': saved_count,
                    'items': items,
                    'preview': items[:5],
                    'sheet_key': sheet_key,
                    'sheet_name': sheet_name,
                    'total_value': total_value,
                    'total_formatted': total_formatted,
                    'currency': project.unidade_monetaria,
                    'message': f'{saved_count} itens importados e salvos com sucesso na aba "{sheet_name}"!'
                }), 200
                
            except ValueError:
                return jsonify({
                    'success': True,
                    'count': len(items),
                    'items': items,
                    'preview': items[:5],
                    'warning': 'project_id inválido. Dados processados mas não salvos no banco.'
                }), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'success': True,
                    'count': len(items),
                    'items': items,
                    'preview': items[:5],
                    'warning': f'Dados processados mas erro ao salvar no banco: {str(e)}'
                }), 200
            
        return jsonify({
            'success': True,
            'count': len(items),
            'items': items,
            'preview': items[:5],
            'message': 'Dados processados com sucesso. Forneça project_id para salvar no banco.'
        }), 200
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/template', methods=['GET'])
def get_template():
    """
    Generate an Excel template for import
    """
    try:
        # Create a simple dataframe
        data = {
            'Descrição': ['Exemplo Item A', 'Exemplo Item B'],
            'Quantidade': [10, 5],
            'Preço Unitário': [5000, 15000],
            'Categoria': ['Mobiliário', 'Informática']
        }
        
        df = pd.DataFrame(data)
        
        # Save to bytes buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Importação')
            
        output.seek(0)
        
        from flask import send_file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='modelo_importacao_viabiliza.xlsx'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


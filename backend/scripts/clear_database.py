"""
Script para limpar todos os registros das tabelas do banco de dados
Mantém a estrutura das tabelas, apenas remove os dados
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.src.app import create_app
from backend.src import db
from backend.src.models.project import Project
from backend.src.models.equipment import Equipment


def clear_database():
    """
    Remove todos os registros de todas as tabelas
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("Limpando banco de dados...")
            print("=" * 60)
            
            # Contar registros antes da limpeza
            equipment_count = Equipment.query.count()
            project_count = Project.query.count()
            
            print(f"\nRegistros encontrados:")
            print(f"  - Projects: {project_count}")
            print(f"  - Equipment: {equipment_count}")
            
            if project_count == 0 and equipment_count == 0:
                print("\n✓ O banco de dados já está vazio.")
                return
            
            # Confirmar antes de deletar
            print(f"\n⚠️  ATENÇÃO: Esta operação irá deletar TODOS os registros!")
            print(f"   - {project_count} projeto(s) serão deletados")
            print(f"   - {equipment_count} equipamento(s) serão deletados")
            
            confirm = input("\nDeseja continuar? (sim/não): ").strip().lower()
            
            if confirm not in ['sim', 's', 'yes', 'y']:
                print("\n✗ Operação cancelada.")
                return
            
            # Deletar todos os equipamentos primeiro (devido à foreign key)
            print("\nDeletando equipamentos...")
            Equipment.query.delete()
            print("✓ Equipamentos deletados.")
            
            # Deletar todos os projetos
            print("Deletando projetos...")
            Project.query.delete()
            print("✓ Projetos deletados.")
            
            # Commit das alterações
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✓ Banco de dados limpo com sucesso!")
            print("=" * 60)
            print("\nTodas as tabelas estão vazias, mas a estrutura foi mantida.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Erro ao limpar banco de dados: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    clear_database()


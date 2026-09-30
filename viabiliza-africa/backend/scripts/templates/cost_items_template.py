"""
Gera template Excel para importação OPEX/CAPEX (UC13).

Uso:
    python -m scripts.templates.cost_items_template
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from openpyxl import Workbook


def main() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "OPEX_CAPEX"
    ws.append(["tipo", "categoria", "descricao", "quantidade", "unidade", "preco_unitario", "fornecedor"])
    ws.append(["capex", "Equipamento", "Servidor Dell PowerEdge", 2, "un", 450000, "TechAngola"])
    ws.append(["opex", "Pessoal", "Salários técnicos (anual)", 12, "mes", 350000, ""])
    ws.append(["opex", "Energia", "Consumo eléctrico mensal", 1, "mes", 85000, "ENDE"])

    out = Path(__file__).resolve().parent / "importacao_opex_capex.xlsx"
    wb.save(out)
    print(f"Template criado: {out}")


if __name__ == "__main__":
    main()

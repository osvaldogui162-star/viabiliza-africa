"""
Business logic and calculation services
"""

from typing import Dict
from ..utils.parsers import parse_value, format_decimal


def calculate_inflation_index(inflation_rate: float, previous_index: float) -> float:
    """
    Calculate Inflation Index
    Formula: Índice de Inflação (n) = (1 + Taxa de Inflação (n)) × Índice de Inflação (n-1)
    
    Args:
        inflation_rate: Inflation rate as percentage (e.g., 2.5 for 2.5%)
        previous_index: Previous year's inflation index
    
    Returns:
        Calculated inflation index
    """
    return (1 + inflation_rate / 100) * previous_index


def calculate_rst(rendimentos: Dict[str, float], percentage: float = 0.0) -> Dict[str, float]:
    """
    Calculate Reserva de Segurança de Tesouraria (RST)
    RST represents the minimum volume of cash needed to face delays in receipts
    and/or forced anticipations of payments. Based on Rendimentos.
    
    Args:
        rendimentos: Dictionary with year keys and revenue values
        percentage: Percentage of revenue to use for RST (if provided)
    
    Returns:
        Dictionary with calculated RST values per year
    """
    rst_values = {}
    
    if percentage > 0:
        # Use percentage of revenue
        for year, revenue in rendimentos.items():
            rst_values[year] = revenue * (percentage / 100)
    else:
        # Default: use average monthly revenue as RST
        # 1.5 months of revenue as safety buffer
        for year, revenue in rendimentos.items():
            monthly_revenue = revenue / 12
            rst_values[year] = monthly_revenue * 1.5
    
    return rst_values


def recalculate_formulas(sheet_data: dict, sheet_name: str) -> dict:
    """
    Recalculate all formulas in the sheet
    
    Args:
        sheet_data: Dictionary containing sheet data
        sheet_name: Name of the sheet
    
    Returns:
        Dictionary with calculated values
    """
    if sheet_name != 'pressupostos':
        return {}
    
    calculated_values = {}
    rows = sheet_data.get('rows', [])
    
    # Find row indices
    row_indices = {}
    for idx, row in enumerate(rows):
        if row and len(row) > 0:
            row_indices[row[0]] = idx
    
    # Get initial inflation index
    if 'Índice de Inflação' in row_indices:
        idx_row = row_indices['Índice de Inflação']
        initial_index = parse_value(rows[idx_row][1] if len(rows[idx_row]) > 1 else '1')
        previous_index = initial_index
        
        # Calculate inflation index for each year
        # Column 1 = 2022 (Inicial), Columns 2-6 = 2023, 2024, 2025, 2026, 2027
        if 'Taxa de Inflação' in row_indices:
            inf_row = row_indices['Taxa de Inflação']
            for col_idx in range(2, min(7, len(rows[inf_row]))):  # Columns 2-6 = 2023-2027
                inflation_rate = parse_value(rows[inf_row][col_idx] if len(rows[inf_row]) > col_idx else '0')
                calculated_index = calculate_inflation_index(inflation_rate, previous_index)
                calculated_values[f'Índice de Inflação-{col_idx}'] = format_decimal(calculated_index)
                previous_index = calculated_index
    
    return calculated_values


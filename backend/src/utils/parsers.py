"""
Utility functions for parsing and formatting values
"""


def parse_value(value: str) -> float:
    """
    Parse a cell value to float, handling percentages and currency
    
    Args:
        value: String value that may contain currency symbols, percentages, etc.
    
    Returns:
        Parsed float value, or 0.0 if parsing fails
    """
    if not value:
        return 0.0
    # Remove currency symbols, commas, spaces, and percentage signs
    cleaned = value.replace('€', '').replace(',', '').replace(' ', '').replace('%', '')
    # Replace comma decimal separator with dot
    cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def format_decimal(value: float, decimals: int = 4) -> str:
    """
    Format a float as decimal string
    
    Args:
        value: Float value to format
        decimals: Number of decimal places
    
    Returns:
        Formatted string
    """
    return f"{value:.{decimals}f}"


def format_percentage(value: float) -> str:
    """
    Format a float as percentage string
    
    Args:
        value: Float value to format
    
    Returns:
        Formatted percentage string (e.g., "2.50%")
    """
    return f"{value:.2f}%"


def format_currency(value: float, symbol: str = "€") -> str:
    """
    Format a float as currency string
    
    Args:
        value: Float value to format
        symbol: Currency symbol
    
    Returns:
        Formatted currency string (e.g., "€1,234.56")
    """
    return f"{symbol}{value:,.2f}"


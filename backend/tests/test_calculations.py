"""
Tests for calculation services
"""

import pytest
from backend.src.services.calculations import calculate_inflation_index, calculate_rst


def test_calculate_inflation_index():
    """Test inflation index calculation"""
    # Test with 2% inflation rate
    result = calculate_inflation_index(2.0, 1.0)
    assert result == 1.02
    
    # Test with 0% inflation
    result = calculate_inflation_index(0.0, 1.0)
    assert result == 1.0
    
    # Test with negative inflation
    result = calculate_inflation_index(-1.0, 1.0)
    assert result == 0.99


def test_calculate_rst():
    """Test RST calculation"""
    rendimentos = {
        'Ano 1': 120000.0,  # 120k per year = 10k per month
        'Ano 2': 144000.0,  # 144k per year = 12k per month
    }
    
    rst = calculate_rst(rendimentos)
    
    # Should be 1.5 months of revenue
    assert rst['Ano 1'] == 15000.0  # 10k * 1.5
    assert rst['Ano 2'] == 18000.0  # 12k * 1.5


def test_calculate_rst_with_percentage():
    """Test RST calculation with percentage"""
    rendimentos = {
        'Ano 1': 100000.0,
    }
    
    rst = calculate_rst(rendimentos, percentage=10.0)
    
    # Should be 10% of revenue
    assert rst['Ano 1'] == 10000.0


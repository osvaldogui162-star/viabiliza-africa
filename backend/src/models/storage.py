"""
Data storage models and operations
"""

import json
import os
from typing import Dict, Any
from pathlib import Path


class DataStorage:
    """Handle data storage operations"""
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize data storage
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_data_file(self, sheet_name: str) -> Path:
        """
        Get the path to the data file for a sheet
        
        Args:
            sheet_name: Name of the sheet
        
        Returns:
            Path to the data file
        """
        return self.data_dir / f'{sheet_name}.json'
    
    def load_sheet_data(self, sheet_name: str) -> Dict[str, Any]:
        """
        Load sheet data from file
        
        Args:
            sheet_name: Name of the sheet
        
        Returns:
            Dictionary with sheet data, or empty dict if file doesn't exist
        """
        file_path = self.get_data_file(sheet_name)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_sheet_data(self, sheet_name: str, data: Dict[str, Any]):
        """
        Save sheet data to file
        
        Args:
            sheet_name: Name of the sheet
            data: Dictionary with sheet data
        """
        file_path = self.get_data_file(sheet_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


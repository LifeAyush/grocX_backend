import json
import logging
from typing import List, Dict, Any
from app.core.config import get_product_mappings
from app.models.request import GroceryItem
from fastapi import Depends

logger = logging.getLogger(__name__)

class ProductMappingService:
    """
    Service for mapping generic product names to platform-specific names and IDs.
    """
    
    def __init__(self, product_mappings: Dict[str, Dict[str, Any]] = Depends(get_product_mappings)):
        self.product_mappings = product_mappings
    
    def map_products(self, items: List[GroceryItem]) -> Dict[str, Dict[str, Any]]:
        """
        Map generic product names to platform-specific names and IDs.
        
        Args:
            items: List of grocery items from the API request
            
        Returns:
            Dictionary mapping generic names to platform-specific details
        """
        mapped_products = {}
        
        for item in items:
            generic_name = item.name.lower()
            
            # Look up the mapping
            if generic_name in self.product_mappings:
                mapped_products[item.name] = self.product_mappings[generic_name]
            else:
                # If no mapping exists, log a warning
                logger.warning(f"No mapping found for product: {item.name}")
                mapped_products[item.name] = {}
        
        return mapped_products

# Example product_mappings.json structure
"""
{
    "milk": {
        "PlatformA": {
            "product_id": "123456",
            "product_name": "Whole Milk 1L"
        },
        "PlatformB": {
            "product_id": "milk-whole-1l",
            "product_name": "Organic Whole Milk (1 Liter)"
        },
        "PlatformC": {
            "product_id": "MILK001",
            "product_name": "Fresh Whole Milk 1L"
        },
        "PlatformD": {
            "product_id": "9876543",
            "product_name": "Whole Milk 1 Liter"
        }
    },
    "bread": {
        "PlatformA": {
            "product_id": "234567",
            "product_name": "White Bread Loaf"
        },
        "PlatformB": {
            "product_id": "bread-white",
            "product_name": "White Sandwich Bread"
        },
        "PlatformC": {
            "product_id": "BREAD001",
            "product_name": "White Bread 500g"
        },
        "PlatformD": {
            "product_id": "8765432",
            "product_name": "Sliced White Bread"
        }
    }
}
"""
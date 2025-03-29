import logging
import numpy as np
from typing import Dict, List, Any
from app.models.request import GroceryItem
from app.core.exceptions import OptimizationError
from decimal import Decimal

logger = logging.getLogger(__name__)

class PriceOptimizerService:
    """
    Service for optimizing the selection of items across platforms to
    create the most cost-effective basket.
    """
    
    def optimize_basket(
        self, 
        price_data: Dict[str, Dict[str, Dict[str, Any]]], 
        requested_items: List[GroceryItem]
    ) -> Dict[str, Any]:
        """
        Optimize the selection of items across platforms for the lowest total cost.
        
        This uses a greedy approach, selecting the lowest-priced item from each category.
        For more complex scenarios (e.g., bundle discounts), this could be enhanced with
        more sophisticated optimization algorithms.
        
        Args:
            price_data: Nested dictionary with price and discount data for all products
            requested_items: Original list of grocery items from the request
            
        Returns:
            Dictionary containing the optimized basket details
        """
        try:
            # Create a quantity map for the requested items
            quantity_map = {item.name: item.quantity for item in requested_items}
            unit_map = {item.name: item.unit for item in requested_items}
            
            # Initialize the optimized basket
            optimized_items = []
            total_original_price = Decimal('0.0')
            total_final_price = Decimal('0.0')
            
            # Process each requested item
            for generic_name, platforms in price_data.items():
                if not platforms:
                    logger.warning(f"No price data available for {generic_name}")
                    continue
                
                # Find the platform with the lowest final price for this item
                best_platform = None
                best_price_data = None
                lowest_price = Decimal('Infinity')
                
                for platform, data in platforms.items():
                    if "final_price" in data and data["final_price"] < lowest_price:
                        lowest_price = data["final_price"]
                        best_platform = platform
                        best_price_data = data
                
                if best_platform and best_price_data:
                    # Calculate total price based on quantity
                    quantity = quantity_map.get(generic_name, 1)
                    item_original_price = best_price_data["original_price"] * quantity
                    item_final_price = best_price_data["final_price"] * quantity
                    item_discount = best_price_data["discount"] * quantity
                    
                    # Add to running totals
                    total_original_price += item_original_price
                    total_final_price += item_final_price
                    
                    # Add the item to the optimized basket
                    optimized_items.append({
                        "name": generic_name,
                        "platform": best_platform,
                        "original_price": item_original_price,
                        "discount": item_discount,
                        "final_price": item_final_price,
                        "quantity": quantity,
                        "unit": unit_map.get(generic_name),
                        "platform_specific_name": best_price_data.get("product_name"),
                        "product_id": best_price_data.get("product_id"),
                        "url": best_price_data.get("url")
                    })
            
            # Calculate total savings
            total_savings = total_original_price - total_final_price
            
            return {
                "total_price": total_final_price,
                "savings": total_savings,
                "items": optimized_items
            }
            
        except Exception as e:
            logger.exception("Error optimizing basket")
            raise OptimizationError(f"Failed to optimize basket: {str(e)}")
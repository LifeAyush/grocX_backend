# request.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class GroceryItem(BaseModel):
    name: str
    quantity: int = Field(default=1, ge=1)
    unit: Optional[str] = None  # e.g., kg, liter, piece

class PriceComparisonRequest(BaseModel):
    items: List[GroceryItem]
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {"name": "Milk", "quantity": 1, "unit": "liter"},
                    {"name": "Bread", "quantity": 2, "unit": "loaf"},
                    {"name": "Eggs", "quantity": 12, "unit": "piece"}
                ]
            }
        }

# response.py
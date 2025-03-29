from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from decimal import Decimal

class ItemPrice(BaseModel):
    name: str
    platform: str
    original_price: Decimal
    discount: Decimal = Decimal('0.0')
    final_price: Decimal
    quantity: int
    unit: Optional[str] = None
    platform_specific_name: Optional[str] = None
    product_id: Optional[str] = None
    url: Optional[str] = None

class OptimizedBasketResponse(BaseModel):
    total_price: Decimal
    savings: Decimal
    items: List[ItemPrice]
    
    class Config:
        schema_extra = {
            "example": {
                "total_price": 15.67,
                "savings": 2.30,
                "items": [
                    {
                        "name": "Milk",
                        "platform": "PlatformA",
                        "original_price": 2.50,
                        "discount": 0.50,
                        "final_price": 2.00,
                        "quantity": 1,
                        "unit": "liter",
                        "platform_specific_name": "Whole Milk 1L",
                        "product_id": "123456",
                        "url": "https://platform-a.com/products/123456"
                    }
                ]
            }
        }
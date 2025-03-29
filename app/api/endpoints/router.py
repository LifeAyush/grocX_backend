from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from app.models.request import PriceComparisonRequest
from app.models.response import OptimizedBasketResponse
from app.services.scraper_manager import ScraperManager
from app.services.price_optimizer import PriceOptimizerService
from app.services.product_mapping import ProductMappingService
from app.core.exceptions import ScrapingError, OptimizationError

router = APIRouter(tags=["prices"])
logger = logging.getLogger(__name__)

@router.post("/get_prices", response_model=OptimizedBasketResponse)
async def get_optimized_prices(
    request: PriceComparisonRequest,
    scraper_manager: ScraperManager = Depends(),
    product_mapping_service: ProductMappingService = Depends(),
    price_optimizer: PriceOptimizerService = Depends()
):
    """
    Get the most cost-effective basket of grocery items across multiple platforms.
    
    This endpoint:
    1. Takes a list of grocery items
    2. Scrapes prices from multiple platforms in parallel
    3. Applies available discounts
    4. Optimizes the selection for the lowest total cost
    5. Returns the optimized basket with detailed pricing
    """
    try:
        # Map generic product names to platform-specific names and IDs
        mapped_products = product_mapping_service.map_products(request.items)
        
        # Fetch prices and discounts concurrently from all platforms
        price_data = await scraper_manager.fetch_all_prices_and_discounts(mapped_products)
        
        # Optimize the basket for lowest total cost
        optimized_basket = price_optimizer.optimize_basket(price_data, request.items)
        
        # Return the optimized basket
        return OptimizedBasketResponse(
            total_price=optimized_basket["total_price"],
            savings=optimized_basket["savings"],
            items=optimized_basket["items"]
        )
    
    except ScrapingError as e:
        logger.error(f"Scraping error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error fetching prices: {str(e)}")
    
    except OptimizationError as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error optimizing basket: {str(e)}")
    
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
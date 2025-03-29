import asyncio
import logging
from typing import Dict, List, Any, Tuple
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.platform_a import PlatformAScraper
from app.scrapers.platform_b import PlatformBScraper
from app.scrapers.platform_c import PlatformCScraper
from app.scrapers.platform_d import PlatformDScraper
from app.core.config import settings
from app.core.exceptions import ScrapingError
from app.utils.async_utils import run_concurrently_with_limit
from fastapi import Depends
from decimal import Decimal

logger = logging.getLogger(__name__)

class ScraperManager:
    """
    Manages scrapers for all platforms and coordinates concurrent scraping.
    """
    
    def __init__(self):
        # Initialize scrapers for all platforms
        self.scrapers: Dict[str, BaseScraper] = {
            "PlatformA": PlatformAScraper(),
            "PlatformB": PlatformBScraper(),
            "PlatformC": PlatformCScraper(),
            "PlatformD": PlatformDScraper(),
        }
    
    async def fetch_all_prices_and_discounts(self, mapped_products: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch prices and discounts for all products from all platforms concurrently.
        
        Args:
            mapped_products: Dictionary mapping generic product names to platform-specific names and IDs
            
        Returns:
            Dictionary containing all price and discount data
        """
        try:
            # Prepare tasks for concurrent execution
            tasks = []
            
            for generic_name, platforms in mapped_products.items():
                for platform, details in platforms.items():
                    if platform in self.scrapers:
                        # Add price scraping task
                        tasks.append((
                            self._fetch_price_and_discount,
                            (
                                generic_name,
                                platform,
                                details["product_id"],
                                details["product_name"]
                            )
                        ))
            
            # Run tasks concurrently with a limit
            results = await run_concurrently_with_limit(
                tasks, 
                limit=settings.MAX_CONCURRENT_REQUESTS
            )
            
            # Process and organize results
            organized_results = {}
            
            for generic_name, platform, result in results:
                if generic_name not in organized_results:
                    organized_results[generic_name] = {}
                    
                organized_results[generic_name][platform] = result
            
            return organized_results
        
        except Exception as e:
            logger.exception("Error in fetch_all_prices_and_discounts")
            raise ScrapingError(f"Failed to fetch prices and discounts: {str(e)}")
    
    async def _fetch_price_and_discount(
        self, 
        generic_name: str, 
        platform: str, 
        product_id: str, 
        product_name: str
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Fetch both price and discount for a single product from a single platform.
        
        Returns:
            Tuple of (generic_name, platform, combined_data)
        """
        scraper = self.scrapers[platform]
        
        # Run price and discount scraping concurrently
        price_task = asyncio.create_task(scraper.get_price(product_id, product_name))
        discount_task = asyncio.create_task(scraper.get_discount(product_id, product_name))
        
        # Wait for both tasks to complete
        price_data, discount_data = await asyncio.gather(price_task, discount_task)
        
        # Calculate final price after discount
        original_price = price_data["price"]
        discount_amount = Decimal('0.0')
        
        if discount_data["discount_type"] == "percentage":
            discount_amount = original_price * (discount_data["discount"] / Decimal('100.0'))
        elif discount_data["discount_type"] == "absolute":
            discount_amount = discount_data["discount"]
        
        final_price = original_price - discount_amount
        
        # Combine the data
        combined_data = {
            **price_data,
            "original_price": original_price,
            "discount": discount_amount,
            "final_price": final_price,
            "generic_name": generic_name
        }
        
        return generic_name, platform, combined_data
    
    async def close(self):
        """Close all scraper sessions."""
        close_tasks = []
        
        for scraper in self.scrapers.values():
            close_tasks.append(scraper.close())
        
        if close_tasks:
            await asyncio.gather(*close_tasks)
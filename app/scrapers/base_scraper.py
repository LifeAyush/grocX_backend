from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import aiohttp
import asyncio
import logging
from app.core.exceptions import ScrapingError
from app.utils.cache import TTLCache
from app.core.config import settings
from decimal import Decimal

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Abstract base class for platform-specific scrapers."""
    
    def __init__(self):
        self.platform_name = self._get_platform_name()
        self.base_url = self._get_base_url()
        self.timeout = settings.SCRAPER_TIMEOUT
        self.cache = TTLCache(ttl=settings.CACHE_TTL)
        self.session = None
    
    @abstractmethod
    def _get_platform_name(self) -> str:
        """Return the name of the platform."""
        pass
    
    @abstractmethod
    def _get_base_url(self) -> str:
        """Return the base URL for the platform."""
        pass
    
    async def _ensure_session(self) -> None:
        """Ensure an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers=self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Return headers for HTTP requests."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    async def get_price(self, product_id: str, product_name: str) -> Dict[str, Any]:
        """
        Get price for a specific product.
        
        Args:
            product_id: Platform-specific product ID
            product_name: Platform-specific product name
            
        Returns:
            Dict containing price information
        """
        cache_key = f"price:{self.platform_name}:{product_id}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for {cache_key}")
            return cached
        
        try:
            await self._ensure_session()
            data = await self._scrape_price(product_id, product_name)
            self.cache.set(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"Error scraping price for {product_name} from {self.platform_name}: {str(e)}")
            raise ScrapingError(f"Failed to scrape price for {product_name} from {self.platform_name}: {str(e)}")
    
    async def get_discount(self, product_id: str, product_name: str) -> Dict[str, Any]:
        """
        Get available discounts for a specific product.
        
        Args:
            product_id: Platform-specific product ID
            product_name: Platform-specific product name
            
        Returns:
            Dict containing discount information
        """
        cache_key = f"discount:{self.platform_name}:{product_id}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for {cache_key}")
            return cached
        
        try:
            await self._ensure_session()
            data = await self._scrape_discount(product_id, product_name)
            self.cache.set(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"Error scraping discount for {product_name} from {self.platform_name}: {str(e)}")
            # Return zero discount instead of failing
            return {"discount": Decimal('0.0'), "discount_type": "none"}
    
    @abstractmethod
    async def _scrape_price(self, product_id: str, product_name: str) -> Dict[str, Any]:
        """
        Platform-specific implementation to scrape product price.
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    async def _scrape_discount(self, product_id: str, product_name: str) -> Dict[str, Any]:
        """
        Platform-specific implementation to scrape product discounts.
        Must be implemented by subclasses.
        """
        pass
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
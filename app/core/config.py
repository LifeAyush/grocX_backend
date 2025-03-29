import json
import os
from pydantic import BaseSettings
from typing import List, Dict, Any, Optional
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "price-comparison-api"
    API_V1_STR: str = "/api/v1"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Scraper settings
    SCRAPER_TIMEOUT: int = 10  # seconds
    MAX_CONCURRENT_REQUESTS: int = 20
    CACHE_TTL: int = 60  # seconds
    
    # Platform URLs
    PLATFORM_A_URL: str
    PLATFORM_B_URL: str
    
    # Path to product mappings
    PRODUCT_MAPPINGS_PATH: str = "data/product_mappings.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

@lru_cache()
def get_product_mappings() -> Dict[str, Dict[str, Any]]:
    """Load product mappings from JSON file."""
    settings = get_settings()
    try:
        with open(settings.PRODUCT_MAPPINGS_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Error loading product mappings: {str(e)}")

settings = get_settings()
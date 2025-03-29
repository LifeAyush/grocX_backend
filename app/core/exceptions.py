class BasePriceComparisonError(Exception):
    """Base exception for all price comparison API errors."""
    pass

class ScrapingError(BasePriceComparisonError):
    """Exception raised when scraping operations fail."""
    pass

class OptimizationError(BasePriceComparisonError):
    """Exception raised when price optimization fails."""
    pass

class MappingError(BasePriceComparisonError):
    """Exception raised when product mapping operations fail."""
    pass

class ConfigurationError(BasePriceComparisonError):
    """Exception raised when there are configuration issues."""
    pass

class RateLimitExceededError(ScrapingError):
    """Exception raised when a platform rate limit is exceeded."""
    pass

class ProductNotFoundError(ScrapingError):
    """Exception raised when a product is not found on a platform."""
    pass
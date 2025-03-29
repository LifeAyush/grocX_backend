import time
from typing import Dict, Any, Optional
import threading

class TTLCache:
    """
    A simple Time-To-Live (TTL) cache implementation.
    
    This cache stores items with an expiration time. Items are automatically
    considered expired after their TTL has passed.
    """
    
    def __init__(self, ttl: int = 60):
        """
        Initialize the TTL cache.
        
        Args:
            ttl: Default Time-To-Live in seconds for cache items
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = ttl
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache if it exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            The cached value, or None if not found or expired
        """
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if item["expires"] > time.time():
                    return item["value"]
                else:
                    # Item is expired, remove it
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set an item in the cache with a specified TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-To-Live in seconds (uses default if not specified)
        """
        expires = time.time() + (ttl if ttl is not None else self.default_ttl)
        with self.lock:
            self.cache[key] = {"value": value, "expires": expires}
    
    def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the item was deleted, False if it didn't exist
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        with self.lock:
            self.cache.clear()
    
    def cleanup(self) -> int:
        """
        Remove all expired items from the cache.
        
        Returns:
            Number of items removed
        """
        now = time.time()
        count = 0
        with self.lock:
            expired_keys = [
                key for key, item in self.cache.items() 
                if item["expires"] <= now
            ]
            for key in expired_keys:
                del self.cache[key]
                count += 1
        return count
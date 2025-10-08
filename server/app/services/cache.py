"""
Caching system with SQLite and Redis support
"""

import hashlib
import json
import sqlite3
import time
from typing import Dict, Any, Optional, Union
import structlog
from ..config import settings

logger = structlog.get_logger()


class CacheInterface:
    """Abstract cache interface"""
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache"""
        pass
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = None) -> bool:
        """Set value in cache"""
        pass
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        pass


class SQLiteCache(CacheInterface):
    """SQLite-based cache implementation"""
    
    def __init__(self, db_path: str = "postpilot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database and tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON cache(expires_at)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("SQLite cache initialized", db_path=self.db_path)
            
        except Exception as e:
            logger.error("Failed to initialize SQLite cache", error=str(e))
            raise
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from SQLite cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT value, expires_at 
                FROM cache 
                WHERE key = ? AND expires_at > ?
            """, (key, time.time()))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                value, expires_at = result
                return json.loads(value)
            
            return None
            
        except Exception as e:
            logger.error("SQLite cache get error", key=key, error=str(e))
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = None) -> bool:
        """Set value in SQLite cache"""
        try:
            ttl = ttl or settings.cache_ttl
            expires_at = time.time() + ttl
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (key, json.dumps(value), time.time(), expires_at))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error("SQLite cache set error", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from SQLite cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error("SQLite cache delete error", key=key, error=str(e))
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM cache")
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error("SQLite cache clear error", error=str(e))
            return False
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM cache WHERE expires_at <= ?", (time.time(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
            
        except Exception as e:
            logger.error("SQLite cache cleanup error", error=str(e))
            return 0


class RedisCache(CacheInterface):
    """Redis-based cache implementation"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.redis_url
        self.redis_client = None
        self.init_redis()
    
    def init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.from_url(self.redis_url)
            
            # Test connection
            self.redis_client.ping()
            
            logger.info("Redis cache initialized", url=self.redis_url)
            
        except Exception as e:
            logger.error("Failed to initialize Redis cache", error=str(e))
            raise
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from Redis cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.error("Redis cache get error", key=key, error=str(e))
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = None) -> bool:
        """Set value in Redis cache"""
        try:
            ttl = ttl or settings.cache_ttl
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
            
        except Exception as e:
            logger.error("Redis cache set error", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            self.redis_client.delete(key)
            return True
            
        except Exception as e:
            logger.error("Redis cache delete error", key=key, error=str(e))
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.redis_client.flushdb()
            return True
            
        except Exception as e:
            logger.error("Redis cache clear error", error=str(e))
            return False


class CacheManager:
    """Cache manager with key generation and TTL management"""
    
    def __init__(self, cache_impl: CacheInterface):
        self.cache = cache_impl
    
    def generate_key(self, text: str, mode: str, persona: str) -> str:
        """Generate deterministic cache key with version"""
        cache_version = "v2"  # Increment this when prompts change
        # Normalize text for consistent hashing
        normalized_text = text.strip().lower()
        
        # Create hash of normalized content with version
        content_hash = hashlib.sha256(
            f"{normalized_text}:{mode}:{persona}:{cache_version}".encode()
        ).hexdigest()
        
        return f"postpilot:{content_hash}"
    
    def get(self, text: str, mode: str, persona: str) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        key = self.generate_key(text, mode, persona)
        return self.cache.get(key)
    
    def set(self, text: str, mode: str, persona: str, result: Dict[str, Any], ttl: int = None) -> bool:
        """Set cached result"""
        key = self.generate_key(text, mode, persona)
        
        # Add metadata
        cache_data = {
            "result": result,
            "cached_at": time.time(),
            "mode": mode,
            "persona": persona,
            "text_hash": hashlib.sha256(text.encode()).hexdigest()[:16]
        }
        
        return self.cache.set(key, cache_data, ttl)
    
    def delete(self, text: str, mode: str, persona: str) -> bool:
        """Delete cached result"""
        key = self.generate_key(text, mode, persona)
        return self.cache.delete(key)
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        return self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Cleanup expired entries"""
        if hasattr(self.cache, 'cleanup_expired'):
            return self.cache.cleanup_expired()
        return 0


def create_cache_manager() -> CacheManager:
    """Create cache manager with appropriate backend"""
    if settings.use_redis:
        try:
            cache_impl = RedisCache()
            logger.info("Using Redis cache")
            return CacheManager(cache_impl)
        except Exception as e:
            logger.warning("Redis cache not available, falling back to SQLite", error=str(e))
    
    # Fallback to SQLite
    cache_impl = SQLiteCache()
    logger.info("Using SQLite cache")
    return CacheManager(cache_impl)


# Global cache manager instance
cache_manager = create_cache_manager()

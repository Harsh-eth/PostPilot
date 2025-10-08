"""
Rate limiting implementation with token bucket algorithm
"""

import time
import asyncio
from typing import Dict, Tuple, Optional
from collections import defaultdict
import structlog
from ..config import settings

logger = structlog.get_logger()


class TokenBucket:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        now = time.time()
        
        # Refill tokens based on time elapsed
        time_elapsed = now - self.last_refill
        tokens_to_add = time_elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
        
        # Check if we have enough tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def get_retry_after(self) -> float:
        """Get seconds until next token is available"""
        if self.tokens >= 1:
            return 0.0
        
        tokens_needed = 1 - self.tokens
        return tokens_needed / self.refill_rate


class RateLimiter:
    """Rate limiter with multiple buckets per client"""
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def _get_bucket_key(self, client_id: str, endpoint: str = None) -> str:
        """Generate bucket key for client and endpoint"""
        if endpoint:
            return f"{client_id}:{endpoint}"
        return client_id
    
    def _cleanup_old_buckets(self):
        """Remove old buckets to prevent memory leaks"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        # Remove buckets that haven't been used in 1 hour
        cutoff_time = now - 3600
        keys_to_remove = []
        
        for key, bucket in self.buckets.items():
            if bucket.last_refill < cutoff_time:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.buckets[key]
        
        self.last_cleanup = now
        logger.debug("Cleaned up old rate limit buckets", removed=len(keys_to_remove))
    
    def is_allowed(self, client_id: str, endpoint: str = None, tokens: int = 1) -> Tuple[bool, float]:
        """
        Check if request is allowed
        
        Returns:
            Tuple[bool, float]: (is_allowed, retry_after_seconds)
        """
        self._cleanup_old_buckets()
        
        bucket_key = self._get_bucket_key(client_id, endpoint)
        
        # Get or create bucket
        if bucket_key not in self.buckets:
            self.buckets[bucket_key] = TokenBucket(
                capacity=settings.rate_limit_requests,
                refill_rate=settings.rate_limit_requests / settings.rate_limit_window
            )
        
        bucket = self.buckets[bucket_key]
        
        # Try to consume tokens
        if bucket.consume(tokens):
            return True, 0.0
        
        # Not allowed, return retry time
        retry_after = bucket.get_retry_after()
        return False, retry_after
    
    def get_status(self, client_id: str, endpoint: str = None) -> Dict[str, any]:
        """Get rate limit status for client"""
        bucket_key = self._get_bucket_key(client_id, endpoint)
        
        if bucket_key not in self.buckets:
            return {
                "allowed": True,
                "remaining": settings.rate_limit_requests,
                "reset_time": time.time() + settings.rate_limit_window
            }
        
        bucket = self.buckets[bucket_key]
        
        return {
            "allowed": bucket.tokens >= 1,
            "remaining": int(bucket.tokens),
            "reset_time": bucket.last_refill + settings.rate_limit_window
        }


class RedisRateLimiter:
    """Redis-based rate limiter for distributed systems"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.redis_url
        self.redis_client = None
        self.init_redis()
    
    def init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            logger.info("Redis rate limiter initialized")
        except Exception as e:
            logger.error("Failed to initialize Redis rate limiter", error=str(e))
            raise
    
    def is_allowed(self, client_id: str, endpoint: str = None, tokens: int = 1) -> Tuple[bool, float]:
        """Check if request is allowed using Redis"""
        try:
            key = f"rate_limit:{client_id}:{endpoint or 'global'}"
            now = time.time()
            window_start = now - settings.rate_limit_window
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiration
            pipe.expire(key, settings.rate_limit_window)
            
            results = pipe.execute()
            current_requests = results[1]
            
            if current_requests < settings.rate_limit_requests:
                return True, 0.0
            
            # Calculate retry time
            oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest_request:
                retry_after = oldest_request[0][1] + settings.rate_limit_window - now
                return False, max(0, retry_after)
            
            return False, settings.rate_limit_window
            
        except Exception as e:
            logger.error("Redis rate limiter error", error=str(e))
            # Fallback to allowing request
            return True, 0.0


def create_rate_limiter():
    """Create appropriate rate limiter based on configuration"""
    if settings.use_redis:
        try:
            return RedisRateLimiter()
        except Exception as e:
            logger.warning("Redis rate limiter not available, falling back to in-memory", error=str(e))
    
    return RateLimiter()


# Global rate limiter instance
rate_limiter = create_rate_limiter()

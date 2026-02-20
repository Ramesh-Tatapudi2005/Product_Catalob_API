import json
from typing import Any, Optional
from src.core.database import redis_client

CACHE_TTL = 60  # 60 seconds TTL as per requirements

async def get_cache(key: str) -> Optional[Any]:
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cache(key: str, value: dict, ttl: int = CACHE_TTL):
    await redis_client.setex(key, ttl, json.dumps(value))

async def invalidate_product_caches(product_id: str = None):
    """
    Invalidates the specific product cache and all paginated list caches.
    """
    # Delete specific product cache if an ID is provided
    if product_id:
        await redis_client.delete(f"products:id:{product_id}")
    
    # Delete all paginated list caches using SCAN
    cursor = 0
    while True:
        cursor, keys = await redis_client.scan(cursor, match="products:all:*", count=100)
        if keys:
            await redis_client.delete(*keys)
        if cursor == 0:
            break
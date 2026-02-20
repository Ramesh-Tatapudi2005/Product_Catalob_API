from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from src.core.config import settings

# MongoDB connection
client = AsyncIOMotorClient(settings.mongo_uri)
db = client.product_catalog
product_collection = db.products

# Redis connection
redis_client = redis.Redis(
    host=settings.redis_host, 
    port=settings.redis_port, 
    decode_responses=True
)
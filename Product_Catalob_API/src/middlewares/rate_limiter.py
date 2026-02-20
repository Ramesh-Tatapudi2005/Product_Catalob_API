from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.database import redis_client

RATE_LIMIT = 100
WINDOW_SIZE = 60  # 1 minute

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract client IP address
        client_ip = request.client.host
        
        # Define the Redis key for this IP
        count_key = f"rate_limit:{client_ip}"
        
        # Increment the request count for this IP
        request_count = await redis_client.incr(count_key)
        
        # If this is the first request, set the expiration window
        if request_count == 1:
            await redis_client.expire(count_key, WINDOW_SIZE)
        
        # Check if the limit is exceeded
        if request_count > RATE_LIMIT:
            # Calculate remaining time for the Retry-After header
            ttl = await redis_client.ttl(count_key)
            retry_after = ttl if ttl > 0 else WINDOW_SIZE
            
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
                headers={"Retry-After": str(retry_after)}
            )
        
        # Proceed to the actual route if under the limit
        response = await call_next(request)
        return response
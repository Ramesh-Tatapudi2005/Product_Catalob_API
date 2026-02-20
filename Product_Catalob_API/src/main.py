from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from src.routes import products
from src.middlewares.rate_limiter import RateLimitMiddleware
from src.core.database import product_collection

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Product Catalog API", version="1.0.0")

# Add the global Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# Include the Product API routes
app.include_router(products.router, prefix="/api/products", tags=["Products"])

# Centralized Error Handling for unexpected internal errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

# Health Check Endpoint for Docker orchestration
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}

# Database Seeding logic that runs on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up. Checking database...")
    
    # Check if the products collection is empty
    count = await product_collection.count_documents({})
    if count == 0:
        logger.info("Database is empty. Seeding with 10 initial products...")
        seed_products = [
            {"name": "Laptop Pro", "description": "High performance laptop", "price": 1299.99, "category": "Electronics", "sku": "ELEC-001", "stock": 50},
            {"name": "Wireless Mouse", "description": "Ergonomic wireless mouse", "price": 49.99, "category": "Electronics", "sku": "ELEC-002", "stock": 200},
            {"name": "Mechanical Keyboard", "description": "RGB mechanical keyboard", "price": 109.99, "category": "Electronics", "sku": "ELEC-003", "stock": 150},
            {"name": "Desk Chair", "description": "Ergonomic office chair", "price": 249.50, "category": "Furniture", "sku": "FURN-001", "stock": 30},
            {"name": "Standing Desk", "description": "Motorized standing desk", "price": 499.00, "category": "Furniture", "sku": "FURN-002", "stock": 15},
            {"name": "Coffee Maker", "description": "Drip coffee maker", "price": 79.99, "category": "Appliances", "sku": "APPL-001", "stock": 100},
            {"name": "Blender", "description": "High-speed blender", "price": 119.50, "category": "Appliances", "sku": "APPL-002", "stock": 80},
            {"name": "Yoga Mat", "description": "Non-slip yoga mat", "price": 29.99, "category": "Fitness", "sku": "FIT-001", "stock": 300},
            {"name": "Dumbbell Set", "description": "Adjustable dumbbells", "price": 199.99, "category": "Fitness", "sku": "FIT-002", "stock": 40},
            {"name": "Water Bottle", "description": "Insulated stainless steel", "price": 24.99, "category": "Accessories", "sku": "ACC-001", "stock": 500}
        ]
        
        # Insert the seed data
        await product_collection.insert_many(seed_products)
        logger.info("Database seeding complete.")
    else:
        logger.info(f"Database already contains {count} products. Skipping seed.")
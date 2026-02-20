from fastapi import APIRouter, HTTPException, Query, Path, status
from typing import Optional
from bson import ObjectId
from datetime import datetime

from src.models.product import ProductCreate, ProductUpdate, ProductInDB
from src.core.database import product_collection
from src.services.cache import get_cache, set_cache, invalidate_product_caches

router = APIRouter()

# Helper function to validate ObjectId
def validate_object_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    return ObjectId(id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    # Enforce unique SKU
    if await product_collection.find_one({"sku": product.sku}):
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    product_dict = product.model_dump()
    product_dict["created_at"] = datetime.utcnow()
    product_dict["updated_at"] = datetime.utcnow()
    
    result = await product_collection.insert_one(product_dict)
    created_product = await product_collection.find_one({"_id": result.inserted_id})
    
    # Invalidate paginated caches
    await invalidate_product_caches()
    
    # Convert ObjectId to string for JSON response
    created_product["_id"] = str(created_product["_id"])
    return created_product

@router.get("/")
async def get_products(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100)
):
    cache_key = f"products:all:page:{page}:limit:{limit}"
    
    # Check Cache
    cached_data = await get_cache(cache_key)
    if cached_data:
        return cached_data

    # If not in cache, query DB
    skip = (page - 1) * limit
    cursor = product_collection.find({}).skip(skip).limit(limit)
    
    products = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        products.append(doc)
        
    total = await product_collection.count_documents({})
    
    response_data = {
        "products": products,
        "total": total,
        "page": page,
        "limit": limit
    }
    
    # Set Cache
    await set_cache(cache_key, response_data)
    return response_data

@router.get("/{id}")
async def get_product(id: str):
    validate_object_id(id)
    cache_key = f"products:id:{id}"
    
    # Check Cache
    cached_data = await get_cache(cache_key)
    if cached_data:
        return cached_data

    product = await product_collection.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product["_id"] = str(product["_id"])
    
    # Set Cache
    await set_cache(cache_key, product)
    return product

@router.put("/{id}")
async def update_product(id: str, product_update: ProductUpdate):
    validate_object_id(id)
    
    # Filter out None values so we only update provided fields
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
        
    update_data["updated_at"] = datetime.utcnow()
    
    result = await product_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Invalidate cache for this specific product and all lists
    await invalidate_product_caches(id)
    
    updated_product = await product_collection.find_one({"_id": ObjectId(id)})
    updated_product["_id"] = str(updated_product["_id"])
    return updated_product

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: str):
    validate_object_id(id)
    
    result = await product_collection.delete_one({"_id": ObjectId(id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Invalidate cache for this specific product and all lists
    await invalidate_product_caches(id)
    return None
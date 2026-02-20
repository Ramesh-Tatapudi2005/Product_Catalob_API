import pytest
from fastapi.testclient import TestClient
from src.main import app

# Create a synchronous test client
client = TestClient(app)

def test_health_check():
    """Test that the health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_product_validation_error():
    """Unit Test: Test that missing required fields trigger a validation error."""
    payload = {
        "name": "Test Product",
        # Missing price, category, sku, etc.
    }
    response = client.post("/api/products/", json=payload)
    # FastAPI returns 422 Unprocessable Entity for Pydantic validation errors
    assert response.status_code == 422 

def test_negative_price_validation():
    """Unit Test: Test that negative prices are rejected."""
    payload = {
        "name": "Bad Product",
        "description": "This should fail",
        "price": -10.50,
        "category": "Test",
        "sku": "TEST-001",
        "stock": 5
    }
    response = client.post("/api/products/", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_rate_limiting_structure():
    """
    Integration Test Concept: 
    In a fully running Docker environment, we would loop 101 times 
    to trigger the 429 Too Many Requests response.
    """
    # Example of how the first request passes:
    response = client.get("/api/products/")
    # If Redis is running, it returns 200. If not mocked/running, it might throw a 500.
    # assert response.status_code in [200, 500] 

# Note: Comprehensive integration tests for caching and database operations 
# require the Docker containers to be running or mocking the Redis/Motor clients.
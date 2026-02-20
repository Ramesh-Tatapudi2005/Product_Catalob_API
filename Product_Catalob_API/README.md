# Product Catalog API

A high-performance, production-ready RESTful API built with Python (FastAPI), MongoDB, and Redis. This system is engineered to handle read-heavy workloads through intelligent caching and protect infrastructure with distributed rate limiting.

## Architecture Overview
This application uses a layered architecture:
* **API Framework:** FastAPI for high performance and automatic data validation (via Pydantic).
* **Database:** MongoDB (using Motor for async operations) to store product documents.
* **Cache & Rate Limiting:** Redis to handle transient data caching (read-heavy operations) and IP-based request throttling.
* **Containerization:** Docker & Docker Compose for orchestration and reproducible environments.

## Tech Stack
* **FastAPI:** Chosen for its asynchronous nature and native support for Pydantic, which provides type safety and high-speed data validation.

* **MongoDB (Motor):** A document-oriented NoSQL database was selected for the product catalog to allow for flexible schema definitions (e.g., varying product attributes).

* **Redis:** Serves a dual purpose as a high-speed cache and a distributed state store for the rate limiter.
## Project Structure
```
product-catalog-api/
├── src/
│   ├── core/
│   │   ├── config.py       # Pydantic settings/env loader
│   │   └── database.py     # Mongo & Redis clients
│   ├── middlewares/
│   │   └── rate_limiter.py # Redis-based IP throttling
│   ├── models/
│   │   └── product.py      # Pydantic/MongoDB schemas
│   ├── routes/
│   │   └── products.py     # CRUD API endpoints
│   ├── services/
│   │   └── cache.py        # Redis get/set/invalidate logic
│   └── main.py             # App entry, error handlers, & seeding
├── tests/
│   └── test_api.py         # Unit & Integration tests
├── .env                    # Your local secrets (DO NOT GIT)
├── .env.example            # Template for others
├── .gitignore              # Files to ignore in Git
├── Dockerfile              # API container instructions
├── docker-compose.yml      # Orchestration (App, Mongo, Redis)
├── README.md               # Documentation
└── requirements.txt        # Python dependencies
## Setup Instructions
```
**Prerequisites:** You must have Docker and Docker Desktop installed and running on your machine.

1. Clone this repository. <https://github.com/Ramesh-Tatapudi2005/Product_Catalob_API>
  - Move to the Project Folder. ```cd Product_Catalob_API```
2. Ensure you have a `.env` file in the root directory (you can copy the contents of `.env.example`).
3. Open your Docker Desktop application.
4. If your IDE supports Docker (like VS Code or PyCharm), you can right-click the `docker-compose.yml` file and select "Compose Up".
   * *(Alternatively, if you must use a terminal, run `docker-compose up --build`)*.
5. The API will automatically be available at `http://localhost:3000`. The database will automatically seed with 10 products if empty.

## Running Tests
Tests are written using `pytest`. To run them:
1. Ensure your virtual environment is active.
2. Install test dependencies: `pip install pytest pytest-asyncio httpx` (or via your IDE's package manager).
3. Run the tests using your IDE's testing tab, or execute `pytest tests/` in your terminal.

## Advanced Features

### Caching Strategy
Redis is used to cache `GET` requests to reduce MongoDB load.
* **TTL:** All cached data has a Time-To-Live of 60 seconds.
* **Keys:** * Single products: `products:id:{id}`
    * Paginated lists: `products:all:page:{page}:limit:{limit}`
* **Invalidation:** Automatic invalidation occurs on `POST`, `PUT`, and `DELETE` operations. Creating or modifying a product automatically clears its specific cache and all paginated list caches to prevent stale data.

### Rate Limiting
A global rate limiter is implemented as a FastAPI Middleware to protect the API from abuse.
* **Algorithm:** Fixed window counter using Redis `INCR` and `EXPIRE`.
* **Limit:** 100 requests per minute, per IP address.
* **Response:** Exceeding the limit returns a `429 Too Many Requests` status with a `Retry-After` header indicating when the window resets.

## API Endpoints

### 1. Create Product
* **POST** `/api/products/`
* **Body:** `{"name": "string", "price": 10.5, "category": "string", "sku": "string", "stock": 5}`
* **Response:** `201 Created`

### 2. Get All Products (Paginated & Cached)
* **GET** `/api/products/?page=1&limit=10`
* **Response:** `200 OK` (Returns products array, total count, page, and limit)

### 3. Get Single Product (Cached)
* **GET** `/api/products/{id}`
* **Response:** `200 OK` or `404 Not Found`

### 4. Update Product
* **PUT** `/api/products/{id}`
* **Body:** Partial product object (e.g., `{"price": 15.0}`)
* **Response:** `200 OK`

### 5. Delete Product
* **DELETE** `/api/products/{id}`
* **Response:** `204 No Content`
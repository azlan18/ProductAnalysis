# Product Analysis API

FastAPI backend for product sentiment analysis and comparison.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys and MongoDB URL
```

3. **Run MongoDB:**
```bash
# Using Docker
docker-compose up -d mongodb

# Or use local MongoDB instance
```

4. **Run the application:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Using Docker Compose

```bash
docker-compose up -d
```

This will start both MongoDB and FastAPI services.

## API Endpoints

### Products

- `POST /api/v1/products` - Create a new product
- `GET /api/v1/products` - Get all products
- `GET /api/v1/products/{product_id}` - Get product analysis
- `POST /api/v1/products/{product_id}/analyze` - Start analysis
- `GET /api/v1/products/{product_id}/status` - Get analysis status

### Comparison

- `POST /api/v1/compare` - Compare 2-4 products
- `GET /api/v1/compare/{comparison_id}` - Get comparison results

### Health

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)

## Environment Variables

See `.env.example` for all required environment variables.

## Project Structure

```
server/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── products.py
│   │       ├── compare.py
│   │       └── status.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   ├── schemas/
│   │   └── product.py
│   ├── services/
│   │   ├── serper_service.py
│   │   ├── firecrawl_service.py
│   │   ├── gemini_service.py
│   │   └── storage_service.py
│   ├── utils/
│   │   └── helpers.py
│   └── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```


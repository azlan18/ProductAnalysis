# Complete Setup Guide - Product Analysis Backend

## ✅ Backend Status: COMPLETE

The backend is fully built and ready to use! All features are implemented:
- ✅ Product creation
- ✅ Product analysis pipeline (Serper → Firecrawl → Gemini)
- ✅ Product comparison
- ✅ Real-time status tracking
- ✅ Beanie database models
- ✅ Comprehensive logging

---

## 🚀 Complete Setup Guide (From Scratch)

### Step 1: Navigate to Server Directory
```bash
cd /Users/azlan18/Desktop/ProductAnalysis/server
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Set Up MongoDB

**Option A: Using Docker (Recommended)**
```bash
# Start MongoDB container
docker-compose up -d mongodb

# Verify MongoDB is running
docker ps
```

**Option B: Local MongoDB**
```bash
# If you have MongoDB installed locally, ensure it's running:
# macOS:
brew services start mongodb-community

# Or start manually:
mongod --dbpath /path/to/data
```

### Step 5: Create .env File
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API keys:
# - SERPER_API_KEY (from https://serper.dev)
# - FIRECRAWL_API_KEY (from https://firecrawl.dev)
# - GEMINI_API_KEY (from https://ai.google.dev)
```

**Required .env variables:**
```env
SERPER_API_KEY=your_key_here
FIRECRAWL_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=product_sentiment
DEBUG=True
```

### Step 6: Run the Server
```bash
# Make sure you're in the server directory and venv is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
Connected to MongoDB: product_sentiment
Beanie initialized with document models
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Testing the API

### Option 1: Using Swagger UI (Easiest)
1. Open browser: `http://localhost:8000/docs`
2. Interactive API documentation with "Try it out" buttons

### Option 2: Using curl/Postman

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

#### 2. Create a Product
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 15 Pro",
    "metadata": {}
  }'
```

**Response:**
```json
{
  "product_id": "iphone-15-pro",
  "product_name": "iPhone 15 Pro",
  "created_at": "2024-01-15T10:30:00",
  "status": "pending",
  "metadata": {}
}
```

#### 3. Start Analysis
```bash
# Replace {product_id} with the actual product_id from step 2
curl -X POST "http://localhost:8000/api/v1/products/iphone-15-pro/analyze"
```

**Response:**
```json
{
  "product_id": "iphone-15-pro",
  "status": "processing",
  "message": "Analysis started"
}
```

#### 4. Check Analysis Status
```bash
curl "http://localhost:8000/api/v1/products/iphone-15-pro/status"
```

**Response:**
```json
{
  "product_id": "iphone-15-pro",
  "stage": "scrape",
  "status": "in_progress",
  "progress": 45,
  "current_step": "Scraped 2/3 pages...",
  "timestamp": "2024-01-15T10:31:00"
}
```

#### 5. Get All Products
```bash
curl "http://localhost:8000/api/v1/products"
```

#### 6. Get Product Analysis (after completion)
```bash
curl "http://localhost:8000/api/v1/products/iphone-15-pro"
```

#### 7. Compare Products
```bash
curl -X POST "http://localhost:8000/api/v1/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "product_ids": ["iphone-15-pro", "samsung-galaxy-s24"]
  }'
```

---

## 📋 Complete Testing Workflow

1. **Create Product:**
   ```
   POST http://localhost:8000/api/v1/products
   Body: {"product_name": "iPhone 15 Pro"}
   ```

2. **Start Analysis:**
   ```
   POST http://localhost:8000/api/v1/products/{product_id}/analyze
   ```

3. **Monitor Status (Poll every 2-3 seconds):**
   ```
   GET http://localhost:8000/api/v1/products/{product_id}/status
   ```

4. **Get Results (when status is "completed"):**
   ```
   GET http://localhost:8000/api/v1/products/{product_id}
   ```

5. **Compare Products (after analyzing 2+ products):**
   ```
   POST http://localhost:8000/api/v1/compare
   Body: {"product_ids": ["product1", "product2"]}
   ```

---

## 📁 Project Structure

```
server/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Config & database
│   ├── models/          # Beanie database models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic (Serper, Firecrawl, Gemini)
│   └── utils/           # Helper functions
├── logs/                # Log files (created automatically)
├── .env                 # Your environment variables (create this)
├── .env.example         # Template for .env
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

---

## 🔍 Logging

Logs are saved to:
- `logs/app.log` - General application logs
- `logs/pipeline.log` - Detailed pipeline execution logs

Watch logs in real-time:
```bash
tail -f logs/pipeline.log
```

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
docker ps
# or
mongosh --eval "db.version()"

# Verify connection string in .env
MONGODB_URL=mongodb://localhost:27017
```

### Import Errors
```bash
# Make sure you're in server directory
cd /Users/azlan18/Desktop/ProductAnalysis/server

# Activate venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Errors
- Check `.env` file exists and has correct keys
- Verify keys are valid (no extra spaces, correct format)
- Restart server after changing .env

---

## ✅ Verification Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows all packages)
- [ ] MongoDB running (port 27017)
- [ ] `.env` file created with API keys
- [ ] Server starts without errors
- [ ] Can access `http://localhost:8000/docs`
- [ ] Health check returns `{"status": "healthy"}`

---

## 🎯 Quick Start Commands

```bash
# Navigate to server
cd /Users/azlan18/Desktop/ProductAnalysis/server

# Setup (first time only)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Start MongoDB (if using Docker)
docker-compose up -d mongodb

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 API Documentation

Once server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

**You're all set! Start testing! 🚀**


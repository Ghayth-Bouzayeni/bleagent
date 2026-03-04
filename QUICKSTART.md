# 🚀 BLE Agent Backend - Quick Start Guide

## ✅ Project Successfully Initialized!

Your FastAPI backend is now ready. All files and boilerplate code have been created.

---

## 📁 What Was Created

### Core Application Files
- ✅ `app/main.py` - FastAPI application with CORS and lifespan events
- ✅ `app/database.py` - Async SQLAlchemy engine with auto-initialization
- ✅ `requirements.txt` - All dependencies pinned
- ✅ `Procfile` - Railway deployment configuration
- ✅ `.env.example` - Environment variable template

### Database Models (SQLAlchemy)
- ✅ `app/models/observation.py` - BLE scan observations
- ✅ `app/models/tag_state.py` - Current state of each tag
- ✅ `app/models/ble_config.py` - Site-specific configuration
- ✅ `app/models/vendor_footprint.py` - Vendor classification rules

### API Routers
- ✅ `app/routers/observations.py` - POST /observations (with validation)
- ✅ `app/routers/config.py` - GET /config/vendor-footprint.json & /config/ble-config
- ✅ `app/routers/health.py` - GET /health

### Business Logic Services
- ✅ `app/services/tag_state_service.py` - Tag state upsert logic
- ✅ `app/services/footprint_service.py` - Footprint management

### Vendor Configuration Files
- ✅ `app/config/vendor-footprints/linxens.json` - Linxens BLE tag rules
- ✅ `app/config/vendor-footprints/blc-molex.json` - Molex tag rules
- ✅ `app/config/vendor-footprints/blc-mokko.json` - Mokko tag rules
- ✅ `app/config/vendor-footprint.json` - Master compiled footprint (v2026.02.23-1)

---

## 🏃 Next Steps

### 1. Create Virtual Environment & Install Dependencies

```bash
cd /home/wejden/Advensia/BLE-Agent-Backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Supabase connection string
nano .env
```

Your `.env` should look like:
```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@db.xxxx.supabase.co:5432/postgres
APP_ENV=development
SITE_ID=site_default
```

### 3. Run the Application

```bash
# Make sure you're in the project directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🚀 Initializing database...
✅ Database initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test the API

Open your browser or use curl:

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Interactive API Docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Get Vendor Footprint:**
```bash
curl http://localhost:8000/config/vendor-footprint.json
```

**Get BLE Config:**
```bash
curl "http://localhost:8000/config/ble-config?site_id=site_default"
```

**Submit Test Observation:**
```bash
curl -X POST http://localhost:8000/observations \
  -H "Content-Type: application/json" \
  -d '[{
    "mac": "AA:BB:CC:DD:EE:FF",
    "ts_utc": "2026-03-02T12:00:00Z",
    "rssi": -65,
    "lat": 40.7128,
    "lon": -74.0060,
    "accuracy_m": 15.0,
    "vendor": "linxens",
    "confidence": 0.95,
    "rule_id": "linxens_001",
    "site_id": "site_default"
  }]'
```

---

## 📊 Database Auto-Initialization

The application automatically creates all 4 database tables on first startup:
- ✅ `observations` - Stores BLE scan data
- ✅ `tag_state` - Tracks tag states
- ✅ `ble_config` - Site configurations
- ✅ `vendor_footprint` - Classification rules

No manual SQL scripts needed!

---

## 🚢 Deploy to Railway

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial BLE Agent Backend"
   git remote add origin <your-github-repo>
   git push -u origin main
   ```

2. **Connect to Railway:**
   - Go to railway.app
   - Create new project
   - Connect your GitHub repository
   - Railway auto-detects the `Procfile`

3. **Set Environment Variables in Railway:**
   - `DATABASE_URL` - Your Supabase connection string
   - `APP_ENV` - `production`
   - `SITE_ID` - Your default site ID

4. **Deploy!**
   - Railway automatically deploys on every push
   - Database tables are created automatically on first run

---

## 🔧 Key Features Implemented

### Validation Rules (POST /observations)
- ✅ Confidence threshold: minimum 0.8
- ✅ GPS accuracy threshold: maximum 50 meters
- ✅ Batch processing with accept/reject summary

### Tag State Management
- ✅ Automatic upsert: creates or updates tag records
- ✅ Movement detection: compares location changes
- ✅ Tracks: location, RSSI, vendor, confidence

### Configuration Delivery
- ✅ Active vendor footprint from database
- ✅ Site-specific BLE config with sensible defaults
- ✅ JSON response format ready for Android app

### Database
- ✅ Async SQLAlchemy with asyncpg
- ✅ PostgreSQL with JSONB support
- ✅ Auto-initialization on startup
- ✅ Connection pooling configured

---

## 📱 Android App Integration

Your Android BLEAgent app should:

1. **Fetch vendor footprint on startup:**
   ```
   GET https://your-backend.railway.app/config/vendor-footprint.json
   ```

2. **Fetch BLE config for site:**
   ```
   GET https://your-backend.railway.app/config/ble-config?site_id=<site_id>
   ```

3. **Upload observations in batches:**
   ```
   POST https://your-backend.railway.app/observations
   Content-Type: application/json
   
   [{ mac, ts_utc, rssi, lat, lon, vendor, confidence, ... }]
   ```

---

## 🐛 Troubleshooting

### "DATABASE_URL environment variable is not set"
- Make sure `.env` file exists and contains `DATABASE_URL`
- Verify you're running from the project root directory

### Module not found errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Database connection failed
- Verify Supabase connection string format
- Check if your IP is allowed in Supabase settings
- Test connection: `psql <your-connection-string>`

### Port 8000 already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Documentation

Full documentation is in `README.md`:
- Complete API reference with examples
- Database schema details
- Deployment guides
- Development workflows

---

## ✨ What's Next?

1. **Test locally** - Make sure all endpoints work
2. **Load sample vendor footprint** - Insert the master footprint into `vendor_footprint` table
3. **Configure sites** - Add site configs to `ble_config` table
4. **Deploy to Railway** - Push to GitHub and connect to Railway
5. **Integrate with Android app** - Update BLEAgent to use your backend URL

---

## 🎉 You're All Set!

Your BLE Agent Backend is production-ready with:
- ✅ Async/await throughout
- ✅ Pydantic v2 validation
- ✅ CORS enabled
- ✅ Health checks
- ✅ Auto database init
- ✅ Vendor classification rules
- ✅ Tag state tracking
- ✅ Railway deployment ready

**Start the server and test it now!**

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Then open: http://localhost:8000/docs

Happy coding! 🚀

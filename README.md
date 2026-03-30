# BLE Agent Backend

FastAPI backend for an IoT smart car parking system that processes BLE tag observations from mobile scanning devices.

## Overview

This backend serves a smartphone BLE scanning app (BLEAgent, built in Android/Kotlin) that detects BLE tags on vehicles and uploads observations to this API. The system classifies BLE tags using vendor-specific fingerprints, tracks tag states, and provides configuration to mobile clients.

## Tech Stack

- **Python 3.11+**
- **FastAPI** + Uvicorn (ASGI web server)
- **SQLAlchemy** (async) + asyncpg for PostgreSQL
- **Supabase** (hosted PostgreSQL)
- **Railway** (deployment platform)

## Features

- ✅ Async BLE observation ingestion with batch processing
- ✅ Vendor classification using configurable fingerprint rules
- ✅ Tag state management (location, RSSI, movement tracking)
- ✅ Site-specific configuration delivery
- ✅ Auto-initialization of database schema on startup
- ✅ CORS-enabled for cross-origin requests
- ✅ Health check endpoint
- ✅ Optional webhook dispatcher: pushes recent tag states every 30s (if `WEBHOOK_URL` is set)

## Project Structure

```
BLE-Agent-Backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # Async SQLAlchemy setup
│   ├── models/                  # SQLAlchemy database models
│   │   ├── observation.py       # Observations table
│   │   ├── tag_state.py         # Tag state table
│   │   ├── ble_config.py        # BLE config table
│   │   └── vendor_footprint.py  # Vendor footprint table
│   ├── routers/                 # API endpoints
│   │   ├── observations.py      # POST /observations
│   │   ├── config.py            # GET /config/*
│   │   └── health.py            # GET /health
│   ├── services/                # Business logic
│   │   ├── tag_state_service.py # Tag state upsert logic
│   │   └── footprint_service.py # Footprint management
│   └── config/
│       └── vendor-footprints/   # Vendor rule JSON files
│           ├── linxens.json
│           ├── blc-molex.json
│           ├── blc-mokko.json
│           └── vendor-footprint.json  # Master compiled footprint
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── Procfile                     # Railway deployment config
└── README.md                    # This file
```

## Local Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database (or Supabase account)
- Git

### Installation Steps

1. **Clone the repository**

   ```bash
   cd /home/wejden/Advensia/BLE-Agent-Backend
   ```

2. **Create and activate virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env and add your DATABASE_URL
   ```

   Example `.env`:

   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   APP_ENV=development
   SITE_ID=site_default
   WEBHOOK_URL=https://your-backend.example.com/webhook   # optional
   WEBHOOK_PERIOD_SECONDS=30                              # optional, defaults to 30
   WEBHOOK_TIMEOUT_SECONDS=5                              # optional
   WEBHOOK_ACTIVE_WINDOW_SECONDS=120                      # optional, only send tags seen in last N seconds
   ```

5. **Run the application**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Database Schema

### `observations`

Stores individual BLE scan observations from mobile devices.

| Column            | Type      | Description                                                    |
| ----------------- | --------- | -------------------------------------------------------------- |
| id                | UUID      | Primary key                                                    |
| **tag_id**        | VARCHAR   | **Unique tag identifier** (BLEcon service data or device name) |
| channel_type      | VARCHAR   | Channel type: blecon/standard/ibeacon                          |
| service_data_hex  | VARCHAR   | BLEcon service data (Moko/Molex)                               |
| local_name        | VARCHAR   | Device name (Linxens)                                          |
| mac               | VARCHAR   | MAC address (reference only, rotates)                          |
| beacon_uuid       | VARCHAR   | iBeacon UUID (reference only)                                  |
| beacon_major      | INTEGER   | iBeacon Major (reference only)                                 |
| beacon_minor      | INTEGER   | iBeacon Minor (reference only)                                 |
| ts_utc            | TIMESTAMP | Observation timestamp (UTC)                                    |
| rssi              | INTEGER   | Signal strength                                                |
| tx_power          | INTEGER   | TX power in dBm (optional)                                     |
| lat               | FLOAT     | Latitude                                                       |
| lon               | FLOAT     | Longitude                                                      |
| accuracy_m        | FLOAT     | GPS accuracy in meters                                         |
| vendor            | VARCHAR   | Detected vendor name                                           |
| confidence        | FLOAT     | Classification confidence (0-1)                                |
| rule_id           | VARCHAR   | Matching rule identifier                                       |
| site_id           | VARCHAR   | Site identifier                                                |
| device_id         | VARCHAR   | Device identifier                                              |
| footprint_version | VARCHAR   | Footprint version used                                         |
| created_at        | TIMESTAMP | Record creation time                                           |

**Tag ID Format:**

- **Moko**: BLEcon service data (e.g., `3b00c60c98ec1b114827aa2e22f8fe2aeecf0300`)
- **Molex**: BLEcon service data (e.g., `0000355ea59f4dfb42f196794fa0d0c9301d0300`)
- **Linxens**: Device name (e.g., `LXSSLBT231`)

### `tag_state`

Maintains current state of each detected BLE tag.

| Column       | Type      | Description                             |
| ------------ | --------- | --------------------------------------- |
| **tag_id**   | VARCHAR   | **Primary key** - Unique tag identifier |
| vendor       | VARCHAR   | Detected vendor                         |
| confidence   | FLOAT     | Classification confidence               |
| rule_id      | VARCHAR   | Rule that matched                       |
| last_lat     | FLOAT     | Last known latitude                     |
| last_lon     | FLOAT     | Last known longitude                    |
| last_rssi    | INTEGER   | Last RSSI value                         |
| last_seen    | TIMESTAMP | Last observation time                   |
| site_id      | VARCHAR   | Associated site                         |
| is_moving    | BOOLEAN   | Movement indicator                      |
| beacon_uuid  | VARCHAR   | iBeacon UUID (reference)                |
| beacon_major | INTEGER   | iBeacon Major (reference)               |
| beacon_minor | INTEGER   | iBeacon Minor (reference)               |
| updated_at   | TIMESTAMP | Last update time                        |

### `ble_config`

Configuration settings per site.

| Column                  | Type      | Description                        |
| ----------------------- | --------- | ---------------------------------- |
| site_id                 | VARCHAR   | Primary key - site identifier      |
| upload_interval_sec     | INTEGER   | Upload interval (seconds)          |
| dedup_window_sec        | INTEGER   | Deduplication window (seconds)     |
| max_batch_size          | INTEGER   | Maximum batch size                 |
| confidence_threshold    | FLOAT     | Minimum confidence threshold       |
| gps_poor_threshold_m    | FLOAT     | GPS accuracy threshold (meters)    |
| footprint_refresh_hours | INTEGER   | Footprint refresh interval (hours) |
| updated_at              | TIMESTAMP | Last update time                   |

### `vendor_footprint`

Stores vendor classification rules.

| Column       | Type      | Description                 |
| ------------ | --------- | --------------------------- |
| id           | SERIAL    | Primary key                 |
| version      | VARCHAR   | Version identifier          |
| rules        | JSONB     | Classification rules (JSON) |
| generated_at | TIMESTAMP | Generation timestamp        |
| is_active    | BOOLEAN   | Active status flag          |

## API Endpoints

### Health Check

**GET** `/health`

Returns application health status.

**Response:**

```json
{
  "status": "ok",
  "version": "1.0.0",
  "env": "development"
}
```

---

### Submit Observations

**POST** `/observations`

Accepts a batch of BLE observation frames. Validates and stores observations, updates tag states.

**Validation Rules:**

- Confidence must be ≥ 0.8
- GPS accuracy must be ≤ 50 meters (if provided)

**Request Body:**

```json
[
  {
    "tag_id": "3b00c60c98ec1b114827aa2e22f8fe2aeecf0300",
    "channel_type": "blecon",
    "service_data_hex": "3b00c60c98ec1b114827aa2e22f8fe2aeecf0300",
    "mac": "F7:42:61:EB:EF:C1",
    "ts_utc": "2026-03-06T12:34:56Z",
    "rssi": -61,
    "tx_power": 4,
    "lat": 40.7128,
    "lon": -74.006,
    "accuracy_m": 15.0,
    "vendor": "blc-moko",
    "confidence": 1.0,
    "rule_id": "moko_001",
    "site_id": "nyc_downtown",
    "device_id": "device_001",
    "footprint_version": "2026.03.06-1"
  },
  {
    "tag_id": "LXSSLBT231",
    "channel_type": "standard",
    "local_name": "LXSSLBT231",
    "mac": "C0:53:58:4C:02:31",
    "ts_utc": "2026-03-06T12:35:00Z",
    "rssi": -70,
    "tx_power": -4,
    "lat": 40.713,
    "lon": -74.0062,
    "accuracy_m": 20.0,
    "vendor": "linxens",
    "confidence": 1.0,
    "rule_id": "linxens_001",
    "site_id": "nyc_downtown",
    "device_id": "device_001",
    "footprint_version": "2026.02.23-1"
  }
]
```

**Response:**

```json
{
  "received": 1,
  "accepted": 1,
  "rejected": 0,
  "message": "Processed 1 observations: 1 accepted, 0 rejected"
}
```

---

### Get Vendor Footprint

**GET** `/config/vendor-footprint.json`

Returns the active vendor classification ruleset.

**Response:**

```json
{
  "version": "2026.02.23-1",
  "generated_at": "2026-03-02T00:00:00Z",
  "rules": [
    {
      "vendor": "linxens",
      "rule_id": "linxens_001",
      "priority": 0,
      "confidence": 1.0,
      "conditions": {
        "local_name": {
          "operator": "starts_with",
          "value": "LXSSLBT"
        },
        "service_uuids": {
          "operator": "contains",
          "value": "0000181a-0000-1000-8000-00805f9b34fb"
        }
      }
    }
  ]
}
```

---

### Get BLE Configuration

**GET** `/config/ble-config?site_id=<site_id>`

Returns BLE scanning configuration for a specific site.

**Query Parameters:**

- `site_id` (required): Site identifier

**Response:**

```json
{
  "site_id": "nyc_downtown",
  "upload_interval_sec": 5,
  "dedup_window_sec": 10,
  "max_batch_size": 200,
  "confidence_threshold": 0.8,
  "gps_poor_threshold_m": 50.0,
  "footprint_refresh_hours": 6
}
```

**Default Values** (if site not found):

- upload_interval_sec: 5
- dedup_window_sec: 10
- max_batch_size: 200
- confidence_threshold: 0.8
- gps_poor_threshold_m: 50.0
- footprint_refresh_hours: 6

---

## Deployment

### Railway Deployment

1. **Connect your GitHub repository to Railway**

2. **Set environment variables in Railway dashboard:**
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string
   - `APP_ENV`: `production`
   - `SITE_ID`: Your default site identifier

3. **Railway will automatically:**
   - Detect the `Procfile`
   - Install dependencies from `requirements.txt`
   - Run the application using Uvicorn

4. **Database initialization happens automatically on first startup**

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://..."
export APP_ENV="production"
export SITE_ID="your_site"

# Run with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when test suite is implemented)
pytest
```

### Code Style

This project follows PEP 8 style guidelines. Format code with:

```bash
pip install black
black app/
```

### Database Migrations

For schema changes, consider using Alembic:

```bash
pip install alembic
alembic init migrations
# Configure alembic.ini with your DATABASE_URL
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/db`
- Check Supabase connection pooling settings
- Ensure IP allowlist includes your deployment IP (Railway)

### Module Import Errors

- Ensure you're running from the project root directory
- Activate virtual environment: `source venv/bin/activate`

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## License

© 2026 Advensia. All rights reserved.

## Support

For issues or questions, contact the development team or open an issue in the repository.

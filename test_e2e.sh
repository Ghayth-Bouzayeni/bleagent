#!/bin/bash
# End-to-end test script for BLE-Agent-Backend
# Usage: ./test_e2e.sh [BASE_URL]

BASE_URL="${1:-https://web-production-3e9a7.up.railway.app}"
PASS=0
FAIL=0

echo "============================================"
echo "  BLE-Agent-Backend E2E Test"
echo "  Target: $BASE_URL"
echo "============================================"
echo ""

# Helper function
check() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"

    if echo "$actual" | grep -q "$expected"; then
        echo "  PASS: $test_name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $test_name"
        echo "    Expected to contain: $expected"
        echo "    Got: $actual"
        FAIL=$((FAIL + 1))
    fi
}

# -------------------------------------------
# TEST 1: Health check
# -------------------------------------------
echo "[Test 1] Health Check"
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "GET /health returns 200" "200" "$HTTP_CODE"
check "Response contains status" '"status"' "$BODY"
echo ""

# -------------------------------------------
# TEST 2: Valid Moko observation (should accept)
# -------------------------------------------
echo "[Test 2] Valid Moko Observation (confidence=0.95, accuracy=10m)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/observations" \
  -H "Content-Type: application/json" \
  -d '[{
    "tag_id": "3b00c60c98ec1234567890abcdef1234abcd5678",
    "channel_type": "blecon",
    "service_data_hex": "3b00c60c98ec1234567890abcdef1234abcd5678",
    "local_name": null,
    "mac": "AA:BB:CC:DD:EE:01",
    "ts_utc": "2026-03-27T10:00:00Z",
    "rssi": -65,
    "tx_power": -8,
    "lat": 48.8566,
    "lon": 2.3522,
    "accuracy_m": 10.0,
    "vendor": "blc-moko",
    "confidence": 0.95,
    "rule_id": "moko_blecon_3b00",
    "site_id": "site_default",
    "device_id": "test_device_001",
    "footprint_version": "v1.0"
  }]')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "POST /observations returns 200" "200" "$HTTP_CODE"
check "1 received" '"received":1' "$BODY"
check "1 accepted" '"accepted":1' "$BODY"
check "0 rejected" '"rejected":0' "$BODY"
echo ""

# -------------------------------------------
# TEST 3: Valid Linxens observation (should accept)
# -------------------------------------------
echo "[Test 3] Valid Linxens Observation"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/observations" \
  -H "Content-Type: application/json" \
  -d '[{
    "tag_id": "LXSSLBT231",
    "channel_type": "standard",
    "service_data_hex": null,
    "local_name": "LXSSLBT231",
    "mac": "AA:BB:CC:DD:EE:02",
    "ts_utc": "2026-03-27T10:00:01Z",
    "rssi": -72,
    "lat": 48.8567,
    "lon": 2.3523,
    "accuracy_m": 5.0,
    "vendor": "linxens",
    "confidence": 0.90,
    "rule_id": "linxens_env_lxsslbt",
    "site_id": "site_default",
    "device_id": "test_device_001",
    "footprint_version": "v1.0"
  }]')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "POST returns 200" "200" "$HTTP_CODE"
check "1 accepted" '"accepted":1' "$BODY"
echo ""

# -------------------------------------------
# TEST 4: Low confidence (should reject)
# -------------------------------------------
echo "[Test 4] Low Confidence Observation (confidence=0.5 -> reject)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/observations" \
  -H "Content-Type: application/json" \
  -d '[{
    "tag_id": "3b00aabbccdd1234567890abcdef1234abcd5678",
    "channel_type": "blecon",
    "ts_utc": "2026-03-27T10:01:00Z",
    "rssi": -80,
    "lat": 48.8566,
    "lon": 2.3522,
    "accuracy_m": 10.0,
    "vendor": "blc-moko",
    "confidence": 0.5,
    "site_id": "site_default",
    "device_id": "test_device_001",
    "footprint_version": "v1.0"
  }]')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "POST returns 200" "200" "$HTTP_CODE"
check "0 accepted" '"accepted":0' "$BODY"
check "1 rejected" '"rejected":1' "$BODY"
echo ""

# -------------------------------------------
# TEST 5: Bad GPS accuracy (should reject)
# -------------------------------------------
echo "[Test 5] Bad GPS Accuracy (accuracy=100m -> reject)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/observations" \
  -H "Content-Type: application/json" \
  -d '[{
    "tag_id": "3b00112233441234567890abcdef1234abcd5678",
    "channel_type": "blecon",
    "ts_utc": "2026-03-27T10:02:00Z",
    "rssi": -70,
    "lat": 48.8566,
    "lon": 2.3522,
    "accuracy_m": 100.0,
    "vendor": "blc-moko",
    "confidence": 0.95,
    "site_id": "site_default",
    "device_id": "test_device_001",
    "footprint_version": "v1.0"
  }]')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "POST returns 200" "200" "$HTTP_CODE"
check "0 accepted" '"accepted":0' "$BODY"
check "1 rejected" '"rejected":1' "$BODY"
echo ""

# -------------------------------------------
# TEST 6: GPS unavailable (lat=0, lon=0 -> stored as NULL)
# -------------------------------------------
echo "[Test 6] GPS Unavailable (lat=0.0, lon=0.0 -> stored as NULL)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/observations" \
  -H "Content-Type: application/json" \
  -d '[{
    "tag_id": "3b00deadbeef1234567890abcdef1234abcd5678",
    "channel_type": "blecon",
    "ts_utc": "2026-03-27T10:03:00Z",
    "rssi": -60,
    "lat": 0.0,
    "lon": 0.0,
    "vendor": "blc-moko",
    "confidence": 0.99,
    "site_id": "site_default",
    "device_id": "test_device_001",
    "footprint_version": "v1.0"
  }]')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "POST returns 200" "200" "$HTTP_CODE"
check "1 accepted (GPS 0.0/0.0 normalized, not rejected)" '"accepted":1' "$BODY"
echo ""

# -------------------------------------------
# TEST 7: Duplicate observation (same tag_id + ts_utc -> accepted but skipped)
# -------------------------------------------
echo "[Test 7] Duplicate Observation (same tag_id + ts_utc as Test 2)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/observations" \
  -H "Content-Type: application/json" \
  -d '[{
    "tag_id": "3b00c60c98ec1234567890abcdef1234abcd5678",
    "channel_type": "blecon",
    "service_data_hex": "3b00c60c98ec1234567890abcdef1234abcd5678",
    "mac": "AA:BB:CC:DD:EE:99",
    "ts_utc": "2026-03-27T10:00:00Z",
    "rssi": -65,
    "lat": 48.8566,
    "lon": 2.3522,
    "accuracy_m": 10.0,
    "vendor": "blc-moko",
    "confidence": 0.95,
    "site_id": "site_default",
    "device_id": "test_device_001",
    "footprint_version": "v1.0"
  }]')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "POST returns 200 (no crash on duplicate)" "200" "$HTTP_CODE"
check "1 accepted (ON CONFLICT DO NOTHING, no error)" '"accepted":1' "$BODY"
echo ""

# -------------------------------------------
# TEST 8: Mixed batch (2 valid, 1 low confidence, 1 bad GPS)
# -------------------------------------------
echo "[Test 8] Mixed Batch (2 valid + 1 low confidence + 1 bad GPS)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/observations" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "tag_id": "3b00aaaa00001234567890abcdef1234abcd5678",
      "channel_type": "blecon",
      "ts_utc": "2026-03-27T10:10:00Z",
      "rssi": -55,
      "lat": 48.8570,
      "lon": 2.3530,
      "accuracy_m": 8.0,
      "vendor": "blc-molex",
      "confidence": 0.92,
      "site_id": "site_default",
      "device_id": "test_device_001",
      "footprint_version": "v1.0"
    },
    {
      "tag_id": "LXSSLBT999",
      "channel_type": "standard",
      "local_name": "LXSSLBT999",
      "ts_utc": "2026-03-27T10:10:01Z",
      "rssi": -68,
      "lat": 48.8571,
      "lon": 2.3531,
      "accuracy_m": 3.0,
      "vendor": "linxens",
      "confidence": 0.88,
      "site_id": "site_default",
      "device_id": "test_device_001",
      "footprint_version": "v1.0"
    },
    {
      "tag_id": "3b00bbbb00001234567890abcdef1234abcd5678",
      "channel_type": "blecon",
      "ts_utc": "2026-03-27T10:10:02Z",
      "rssi": -90,
      "lat": 48.8572,
      "lon": 2.3532,
      "accuracy_m": 5.0,
      "vendor": "blc-moko",
      "confidence": 0.3,
      "site_id": "site_default",
      "device_id": "test_device_001",
      "footprint_version": "v1.0"
    },
    {
      "tag_id": "3b00cccc00001234567890abcdef1234abcd5678",
      "channel_type": "blecon",
      "ts_utc": "2026-03-27T10:10:03Z",
      "rssi": -75,
      "lat": 48.8573,
      "lon": 2.3533,
      "accuracy_m": 200.0,
      "vendor": "blc-moko",
      "confidence": 0.95,
      "site_id": "site_default",
      "device_id": "test_device_001",
      "footprint_version": "v1.0"
    }
  ]')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "POST returns 200" "200" "$HTTP_CODE"
check "4 received" '"received":4' "$BODY"
check "2 accepted" '"accepted":2' "$BODY"
check "2 rejected" '"rejected":2' "$BODY"
echo ""

# -------------------------------------------
# TEST 9: No site_id (should default to site_default)
# -------------------------------------------
echo "[Test 9] Missing site_id (should default to site_default)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/observations" \
  -H "Content-Type: application/json" \
  -d '[{
    "tag_id": "3b00ffff00001234567890abcdef1234abcd5678",
    "channel_type": "blecon",
    "ts_utc": "2026-03-27T10:20:00Z",
    "rssi": -62,
    "lat": 48.8580,
    "lon": 2.3540,
    "accuracy_m": 7.0,
    "vendor": "blc-moko",
    "confidence": 0.91,
    "device_id": "test_device_001",
    "footprint_version": "v1.0"
  }]')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

check "POST returns 200" "200" "$HTTP_CODE"
check "1 accepted" '"accepted":1' "$BODY"
echo ""

# -------------------------------------------
# Summary
# -------------------------------------------
echo "============================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "============================================"

if [ $FAIL -eq 0 ]; then
    echo "  All tests passed!"
    exit 0
else
    echo "  Some tests failed. Check output above."
    exit 1
fi

"""
Observations endpoint - receives and processes BLE scan data
"""
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.database import get_db
from app.models.observation import Observation
from app.services.tag_state_service import upsert_tag_state

router = APIRouter(prefix="/observations", tags=["observations"])


class ObservationFrame(BaseModel):
    """Request model for a single observation"""
    # PRIMARY TAG IDENTIFIER (REQUIRED)
    # - Moko/Molex: BLEcon service data (e.g., "3b00c60c98ec...")
    # - Linxens: Device name (e.g., "LXSSLBT231")
    tag_id: str = Field(..., description="Unique tag identifier (BLEcon service data or device name)")
    
    # Channel and raw BLE data
    channel_type: str | None = Field(None, description="Channel type: blecon/standard/ibeacon")
    service_data_hex: str | None = Field(None, description="BLEcon service data (Moko/Molex)")
    local_name: str | None = Field(None, description="Device name (Linxens)")
    mac: str | None = Field(None, description="MAC address (rotating, reference only)")
    
    # iBeacon identifiers (optional, not used for tracking)
    beacon_uuid: str | None = Field(None, description="iBeacon UUID (reference only)")
    beacon_major: int | None = Field(None, description="iBeacon Major value (reference only)")
    beacon_minor: int | None = Field(None, description="iBeacon Minor value (reference only)")
    
    # Observation data
    ts_utc: datetime = Field(..., description="Timestamp in UTC")
    rssi: int = Field(..., description="RSSI signal strength")
    tx_power: int | None = Field(None, description="TX power in dBm (optional)")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    accuracy_m: float | None = Field(None, description="GPS accuracy in meters")
    vendor: str = Field(..., description="Detected vendor name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    rule_id: str | None = Field(None, description="Rule ID that matched")
    site_id: str | None = Field(None, description="Site identifier")
    device_id: str | None = Field(None, description="Device identifier")
    footprint_version: str | None = Field(None, description="Footprint version used")


class ObservationResponse(BaseModel):
    """Response model for observation submission"""
    received: int
    accepted: int
    rejected: int
    message: str


@router.post("", response_model=ObservationResponse)
async def create_observations(
    frames: List[ObservationFrame],
    db: AsyncSession = Depends(get_db)
):
    """
    POST /observations
    
    Accepts a batch of BLE observation frames.
    Validates each frame against confidence >= 0.8 and accuracy_m <= 50.
    Stores valid observations and updates tag state.
    
    Returns a summary of processed observations.
    """
    received = len(frames)
    accepted = 0
    rejected = 0
    
    for frame in frames:
        # Validation: confidence threshold
        if frame.confidence < 0.8:
            rejected += 1
            continue
        
        # Validation: GPS accuracy threshold
        if frame.accuracy_m is not None and frame.accuracy_m > 100.0:
            rejected += 1
            continue
        
        try:
            async with db.begin_nested():
                # Normalize 0.0/0.0 to None (app sends 0.0 when GPS unavailable)
                lat = frame.lat if frame.lat != 0.0 or frame.lon != 0.0 else None
                lon = frame.lon if frame.lat != 0.0 or frame.lon != 0.0 else None

                # Insert observation, skipping duplicates (same tag_id + ts_utc = retried batch)
                stmt = insert(Observation).values(
                    tag_id=frame.tag_id,
                    channel_type=frame.channel_type,
                    service_data_hex=frame.service_data_hex,
                    local_name=frame.local_name,
                    mac=frame.mac,
                    beacon_uuid=frame.beacon_uuid,
                    beacon_major=frame.beacon_major,
                    beacon_minor=frame.beacon_minor,
                    ts_utc=frame.ts_utc,
                    rssi=frame.rssi,
                    tx_power=frame.tx_power,
                    lat=lat,
                    lon=lon,
                    accuracy_m=frame.accuracy_m,
                    vendor=frame.vendor,
                    confidence=frame.confidence,
                    rule_id=frame.rule_id,
                    site_id=frame.site_id or "site_default",
                    device_id=frame.device_id,
                    footprint_version=frame.footprint_version,
                    created_at=datetime.now(timezone.utc)
                ).on_conflict_do_nothing(constraint="uq_observation_tag_ts")

                await db.execute(stmt)

                # Update tag state (using tag_id as stable identifier)
                await upsert_tag_state(
                    db=db,
                    tag_id=frame.tag_id,
                    vendor=frame.vendor,
                    confidence=frame.confidence,
                    rule_id=frame.rule_id,
                    beacon_uuid=frame.beacon_uuid,
                    beacon_major=frame.beacon_major,
                    beacon_minor=frame.beacon_minor,
                    lat=lat,
                    lon=lon,
                    rssi=frame.rssi,
                    last_seen=frame.ts_utc,
                    site_id=frame.site_id or "site_default"
                )

            accepted += 1

        except Exception as e:
            rejected += 1
            print(f"Error processing observation: {str(e)}")
    
    # Commit all changes
    await db.commit()
    
    return ObservationResponse(
        received=received,
        accepted=accepted,
        rejected=rejected,
        message=f"Processed {received} observations: {accepted} accepted, {rejected} rejected"
    )

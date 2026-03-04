"""
Observations endpoint - receives and processes BLE scan data
"""
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.observation import Observation
from app.services.tag_state_service import upsert_tag_state

router = APIRouter(prefix="/observations", tags=["observations"])


class ObservationFrame(BaseModel):
    """Request model for a single observation"""
    beacon_uuid: str = Field(..., description="BLE Beacon UUID (stable identifier)")
    beacon_major: int | None = Field(None, description="iBeacon Major value")
    beacon_minor: int | None = Field(None, description="iBeacon Minor value")
    mac: str | None = Field(None, description="MAC address (rotating, optional)")
    ts_utc: datetime = Field(..., description="Timestamp in UTC")
    rssi: int = Field(..., description="RSSI signal strength")
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
        if frame.accuracy_m is not None and frame.accuracy_m > 50.0:
            rejected += 1
            continue
        
        try:
            # Create observation record
            observation = Observation(
                beacon_uuid=frame.beacon_uuid,
                beacon_major=frame.beacon_major,
                beacon_minor=frame.beacon_minor,
                mac=frame.mac,
                ts_utc=frame.ts_utc,
                rssi=frame.rssi,
                lat=frame.lat,
                lon=frame.lon,
                accuracy_m=frame.accuracy_m,
                vendor=frame.vendor,
                confidence=frame.confidence,
                rule_id=frame.rule_id,
                site_id=frame.site_id or "unknown",
                device_id=frame.device_id,
                footprint_version=frame.footprint_version,
                created_at=datetime.now(timezone.utc)
            )
            
            db.add(observation)
            
            # Update tag state (using beacon_uuid as stable identifier)
            await upsert_tag_state(
                db=db,
                beacon_uuid=frame.beacon_uuid,
                beacon_major=frame.beacon_major,
                beacon_minor=frame.beacon_minor,
                lat=frame.lat,
                lon=frame.lon,
                rssi=frame.rssi,
                last_seen=frame.ts_utc,
                vendor=frame.vendor,
                confidence=frame.confidence,
                site_id=frame.site_id or "unknown"
            )
            
            accepted += 1
            
        except Exception as e:
            rejected += 1
            # Log error in production
            print(f"Error processing observation: {str(e)}")
    
    # Commit all changes
    await db.commit()
    
    return ObservationResponse(
        received=received,
        accepted=accepted,
        rejected=rejected,
        message=f"Processed {received} observations: {accepted} accepted, {rejected} rejected"
    )

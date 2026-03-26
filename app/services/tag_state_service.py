"""
Tag State Service - manages tag state updates
"""
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tag_state import TagState


async def upsert_tag_state(
    db: AsyncSession,
    tag_id: str,
    vendor: str,
    confidence: float,
    rule_id: str | None,
    beacon_uuid: str | None,
    beacon_major: int | None,
    beacon_minor: int | None,
    lat: float | None,
    lon: float | None,
    rssi: int,
    last_seen: datetime,
    site_id: str
) -> TagState:
    """
    Upsert tag state record.
    
    If tag exists, updates its state with new observation data.
    If tag doesn't exist, creates a new record.
    
    Args:
        db: Database session
        tag_id: Unique tag identifier (BLEcon service data or device name)
        vendor: Detected vendor
        confidence: Classification confidence
        rule_id: Rule ID that matched
        beacon_uuid: iBeacon UUID (optional, reference only)
        beacon_major: iBeacon Major value (optional, reference only)
        beacon_minor: iBeacon Minor value (optional, reference only)
        lat: Latitude (None if GPS unavailable)
        lon: Longitude (None if GPS unavailable)
        rssi: RSSI signal strength
        last_seen: Timestamp of last observation
        site_id: Site identifier
    
    Returns:
        Updated or created TagState instance
    """
    # Check if tag state exists
    stmt = select(TagState).where(TagState.tag_id == tag_id)
    result = await db.execute(stmt)
    tag_state = result.scalar_one_or_none()
    
    if tag_state:
        # Update existing tag state
        tag_state.vendor = vendor
        tag_state.confidence = confidence
        tag_state.rule_id = rule_id
        tag_state.beacon_uuid = beacon_uuid
        tag_state.beacon_major = beacon_major
        tag_state.beacon_minor = beacon_minor
        # Only update location if GPS was available
        if lat is not None and lon is not None:
            tag_state.last_lat = lat
            tag_state.last_lon = lon
        tag_state.last_rssi = rssi
        tag_state.last_seen = last_seen
        tag_state.site_id = site_id
        tag_state.updated_at = datetime.now(timezone.utc)
    else:
        # Create new tag state
        tag_state = TagState(
            tag_id=tag_id,
            vendor=vendor,
            confidence=confidence,
            rule_id=rule_id,
            beacon_uuid=beacon_uuid,
            beacon_major=beacon_major,
            beacon_minor=beacon_minor,
            last_lat=lat,       # None if GPS unavailable
            last_lon=lon,       # None if GPS unavailable
            last_rssi=rssi,
            last_seen=last_seen,
            site_id=site_id,
            is_moving=False,
            updated_at=datetime.now(timezone.utc)
        )
        db.add(tag_state)
    
    return tag_state


async def get_tag_state(db: AsyncSession, tag_id: str) -> TagState | None:
    """
    Get tag state by tag_id
    
    Args:
        db: Database session
        tag_id: Unique tag identifier (BLEcon service data or device name)
    
    Returns:
        TagState instance or None if not found
    """
    stmt = select(TagState).where(TagState.tag_id == tag_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

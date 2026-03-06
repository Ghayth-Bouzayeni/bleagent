"""
TagState model - maintains current state of each detected BLE tag
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, TIMESTAMP
from app.database import Base


class TagState(Base):
    __tablename__ = "tag_state"

    # PRIMARY TAG IDENTIFIER
    # - Moko/Molex: BLEcon service data (e.g., "3b00c60c98ec...")
    # - Linxens: Device name (e.g., "LXSSLBT231")
    tag_id = Column(String, primary_key=True)
    
    # Vendor information
    vendor = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    rule_id = Column(String, nullable=True)
    
    # State tracking
    last_lat = Column(Float, nullable=True)
    last_lon = Column(Float, nullable=True)
    last_rssi = Column(Integer, nullable=True)
    last_seen = Column(TIMESTAMP(timezone=True), nullable=True)
    site_id = Column(String, nullable=True, index=True)
    is_moving = Column(Boolean, default=False)
    
    # Optional: Store iBeacon data for reference (not used for tracking)
    beacon_uuid = Column(String, nullable=True)
    beacon_major = Column(Integer, nullable=True)
    beacon_minor = Column(Integer, nullable=True)
    
    # Metadata
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<TagState(tag_id={self.tag_id}, vendor={self.vendor}, last_seen={self.last_seen})>"

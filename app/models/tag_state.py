"""
TagState model - maintains current state of each detected BLE tag
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, TIMESTAMP
from app.database import Base


class TagState(Base):
    __tablename__ = "tag_state"

    # Use beacon UUID as primary key (stable identifier)
    beacon_uuid = Column(String, primary_key=True)
    beacon_major = Column(Integer, nullable=True)
    beacon_minor = Column(Integer, nullable=True)
    
    # State tracking
    last_lat = Column(Float, nullable=True)
    last_lon = Column(Float, nullable=True)
    last_rssi = Column(Integer, nullable=True)
    last_seen = Column(TIMESTAMP(timezone=True), nullable=True)
    vendor = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    site_id = Column(String, nullable=True, index=True)
    is_moving = Column(Boolean, default=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<TagState(beacon_uuid={self.beacon_uuid}, vendor={self.vendor}, last_seen={self.last_seen})>"

"""
Observation model - stores BLE scan observations from mobile devices
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Observation(Base):
    __tablename__ = "observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Stable BLE Beacon Identifiers (use these for tracking)
    beacon_uuid = Column(String, nullable=True, index=True)  # iBeacon UUID
    beacon_major = Column(Integer, nullable=True)            # iBeacon Major
    beacon_minor = Column(Integer, nullable=True)            # iBeacon Minor
    
    # Alternative: Eddystone identifiers
    namespace_id = Column(String, nullable=True)             # Eddystone Namespace
    instance_id = Column(String, nullable=True)              # Eddystone Instance
    
    # MAC address (unstable, for reference only)
    mac = Column(String, nullable=True)                      # Rotating MAC (not for tracking!)
    
    # Observation data
    ts_utc = Column(TIMESTAMP(timezone=True), nullable=False)
    rssi = Column(Integer, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    accuracy_m = Column(Float, nullable=True)
    vendor = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    rule_id = Column(String, nullable=True)
    site_id = Column(String, nullable=False, index=True)
    device_id = Column(String, nullable=True)
    footprint_version = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Observation(beacon_uuid={self.beacon_uuid}, vendor={self.vendor}, rssi={self.rssi})>"

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
    
    # PRIMARY TAG IDENTIFIER (REQUIRED)
    # - Moko/Molex: BLEcon service data (e.g., "3b00c60c98ec...")
    # - Linxens: Device name (e.g., "LXSSLBT231")
    tag_id = Column(String, nullable=False, index=True)
    
    # Channel and raw BLE data
    channel_type = Column(String, nullable=True)             # "blecon", "standard", "ibeacon"
    service_data_hex = Column(String, nullable=True)         # BLEcon service data (Moko/Molex)
    local_name = Column(String, nullable=True)               # Device name (Linxens)
    mac = Column(String, nullable=True)                      # MAC address (reference only, rotates!)
    
    # iBeacon identifiers (optional, stored but not used for tracking Moko/Molex)
    beacon_uuid = Column(String, nullable=True)              # iBeacon UUID (reference only)
    beacon_major = Column(Integer, nullable=True)            # iBeacon Major (reference only)
    beacon_minor = Column(Integer, nullable=True)            # iBeacon Minor (reference only)
    
    # Eddystone identifiers (optional, for future use)
    namespace_id = Column(String, nullable=True)             # Eddystone Namespace
    instance_id = Column(String, nullable=True)              # Eddystone Instance
    
    # Observation data
    ts_utc = Column(TIMESTAMP(timezone=True), nullable=False)
    rssi = Column(Integer, nullable=False)
    tx_power = Column(Integer, nullable=True)                # TX power (dBm) - optional
    lat = Column(Float, nullable=True)                      # None when GPS unavailable (app sends 0.0)
    lon = Column(Float, nullable=True)                      # None when GPS unavailable (app sends 0.0)
    accuracy_m = Column(Float, nullable=True)
    vendor = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    rule_id = Column(String, nullable=True)
    site_id = Column(String, nullable=False, index=True)
    device_id = Column(String, nullable=True)
    footprint_version = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Observation(tag_id={self.tag_id}, vendor={self.vendor}, rssi={self.rssi})>"

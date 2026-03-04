"""
BLEConfig model - configuration settings per site
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, TIMESTAMP
from app.database import Base


class BLEConfig(Base):
    __tablename__ = "ble_config"

    site_id = Column(String, primary_key=True)
    upload_interval_sec = Column(Integer, nullable=False, default=5)
    dedup_window_sec = Column(Integer, nullable=False, default=10)
    max_batch_size = Column(Integer, nullable=False, default=200)
    confidence_threshold = Column(Float, nullable=False, default=0.8)
    gps_poor_threshold_m = Column(Float, nullable=False, default=50.0)
    footprint_refresh_hours = Column(Integer, nullable=False, default=6)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<BLEConfig(site_id={self.site_id})>"

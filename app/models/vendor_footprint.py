"""
VendorFootprint model - stores vendor classification rules
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class VendorFootprint(Base):
    __tablename__ = "vendor_footprint"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String, nullable=False, unique=True, index=True)
    rules = Column(JSONB, nullable=False)
    generated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, nullable=False, default=False, index=True)

    def __repr__(self):
        return f"<VendorFootprint(version={self.version}, is_active={self.is_active})>"

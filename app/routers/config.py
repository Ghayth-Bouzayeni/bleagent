"""
Configuration endpoints - serves vendor footprint and BLE config
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.vendor_footprint import VendorFootprint
from app.models.ble_config import BLEConfig

router = APIRouter(prefix="/config", tags=["config"])


class VendorFootprintResponse(BaseModel):
    """Response model for vendor footprint"""
    version: str
    generated_at: str
    rules: list[Dict[str, Any]]


class BLEConfigResponse(BaseModel):
    """Response model for BLE configuration"""
    site_id: str
    upload_interval_sec: int = Field(..., description="Upload interval in seconds")
    dedup_window_sec: int = Field(..., description="Deduplication window in seconds")
    max_batch_size: int = Field(..., description="Maximum batch size")
    confidence_threshold: float = Field(..., description="Minimum confidence threshold")
    gps_poor_threshold_m: float = Field(..., description="GPS poor accuracy threshold in meters")
    footprint_refresh_hours: int = Field(..., description="Footprint refresh interval in hours")


@router.get("/vendor-footprint.json", response_model=VendorFootprintResponse)
async def get_vendor_footprint(db: AsyncSession = Depends(get_db)):
    """
    GET /config/vendor-footprint.json
    
    Returns the active vendor footprint rules for BLE tag classification.
    Queries the vendor_footprint table for is_active = true.
    """
    # Query for active footprint
    stmt = select(VendorFootprint).where(VendorFootprint.is_active == True)
    result = await db.execute(stmt)
    footprint = result.scalar_one_or_none()
    
    if not footprint:
        # Return empty/default footprint if none active
        return VendorFootprintResponse(
            version="none",
            generated_at="",
            rules=[]
        )
    
    return VendorFootprintResponse(
        version=footprint.version,
        generated_at=footprint.generated_at.isoformat(),
        rules=footprint.rules
    )


@router.get("/ble-config", response_model=BLEConfigResponse)
async def get_ble_config(
    site_id: str = Query(..., description="Site identifier"),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /config/ble-config?site_id=<site_id>
    
    Returns BLE configuration settings for a specific site.
    If site config not found, returns sensible MVP defaults.
    """
    # Query for site config
    stmt = select(BLEConfig).where(BLEConfig.site_id == site_id)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if not config:
        # Return MVP defaults
        return BLEConfigResponse(
            site_id=site_id,
            upload_interval_sec=5,
            dedup_window_sec=10,
            max_batch_size=200,
            confidence_threshold=0.8,
            gps_poor_threshold_m=50.0,
            footprint_refresh_hours=6
        )
    
    return BLEConfigResponse(
        site_id=config.site_id,
        upload_interval_sec=config.upload_interval_sec,
        dedup_window_sec=config.dedup_window_sec,
        max_batch_size=config.max_batch_size,
        confidence_threshold=config.confidence_threshold,
        gps_poor_threshold_m=config.gps_poor_threshold_m,
        footprint_refresh_hours=config.footprint_refresh_hours
    )

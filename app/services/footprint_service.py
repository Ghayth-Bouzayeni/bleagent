"""
Footprint Service - manages vendor footprint data
"""
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vendor_footprint import VendorFootprint


async def get_active_footprint(db: AsyncSession) -> VendorFootprint | None:
    """
    Get the currently active vendor footprint
    
    Args:
        db: Database session
    
    Returns:
        Active VendorFootprint instance or None if not found
    """
    stmt = select(VendorFootprint).where(VendorFootprint.is_active == True)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def set_active_footprint(db: AsyncSession, version: str) -> VendorFootprint | None:
    """
    Set a specific footprint version as active.
    Deactivates all other footprints.
    
    Args:
        db: Database session
        version: Version string of the footprint to activate
    
    Returns:
        Activated VendorFootprint instance or None if version not found
    """
    # Deactivate all footprints
    stmt = select(VendorFootprint)
    result = await db.execute(stmt)
    all_footprints = result.scalars().all()
    
    for fp in all_footprints:
        fp.is_active = False
    
    # Activate the specified version
    stmt = select(VendorFootprint).where(VendorFootprint.version == version)
    result = await db.execute(stmt)
    target_footprint = result.scalar_one_or_none()
    
    if target_footprint:
        target_footprint.is_active = True
        await db.commit()
    
    return target_footprint


async def create_footprint(
    db: AsyncSession,
    version: str,
    rules: list[Dict[str, Any]],
    is_active: bool = False
) -> VendorFootprint:
    """
    Create a new vendor footprint
    
    Args:
        db: Database session
        version: Version string
        rules: List of classification rules
        is_active: Whether this footprint should be active
    
    Returns:
        Created VendorFootprint instance
    """
    footprint = VendorFootprint(
        version=version,
        rules=rules,
        is_active=is_active
    )
    
    db.add(footprint)
    await db.commit()
    await db.refresh(footprint)
    
    return footprint

"""
Periodic webhook dispatcher to push recent tag state snapshots.
Sends tag_state rows seen within a recency window as JSON every interval without blocking request handling.
"""
import os
import asyncio
from datetime import datetime, timedelta, timezone
import httpx
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.tag_state import TagState

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PERIOD_SECONDS = int(os.getenv("WEBHOOK_PERIOD_SECONDS", "30"))
WEBHOOK_TIMEOUT_SECONDS = int(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "5"))
WEBHOOK_ACTIVE_WINDOW_SECONDS = int(os.getenv("WEBHOOK_ACTIVE_WINDOW_SECONDS", "120"))


async def _collect_tag_states() -> list[dict]:
    """Fetch tag_state rows seen recently and serialize to JSON-friendly dicts."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=WEBHOOK_ACTIVE_WINDOW_SECONDS)
    async with AsyncSessionLocal() as session:
        stmt = select(TagState).where(TagState.last_seen.isnot(None)).where(TagState.last_seen >= cutoff)
        result = await session.execute(stmt)
        rows = result.scalars().all()
    payload = []
    for row in rows:
        payload.append(
            {
                "tag_id": row.tag_id,
                "vendor": row.vendor,
                "confidence": row.confidence,
                "rule_id": row.rule_id,
                "last_lat": row.last_lat,
                "last_lon": row.last_lon,
                "last_rssi": row.last_rssi,
                "last_seen": row.last_seen.isoformat() if row.last_seen else None,
                "site_id": row.site_id,
                "is_moving": row.is_moving,
                "beacon_uuid": row.beacon_uuid,
                "beacon_major": row.beacon_major,
                "beacon_minor": row.beacon_minor,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
        )
    return payload


async def _dispatch_once(client: httpx.AsyncClient) -> None:
    payload = await _collect_tag_states()
    if not payload:
        return
    try:
        await client.post(WEBHOOK_URL, json=payload, timeout=WEBHOOK_TIMEOUT_SECONDS)
    except Exception as exc:
        # Log and continue; we intentionally do not raise to avoid stopping the loop.
        print(f"Webhook dispatch failed: {exc}")


async def _dispatch_loop(stop_event: asyncio.Event) -> None:
    if not WEBHOOK_URL:
        print("Webhook dispatcher disabled: WEBHOOK_URL not set")
        return

    async with httpx.AsyncClient() as client:
        while not stop_event.is_set():
            await _dispatch_once(client)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=WEBHOOK_PERIOD_SECONDS)
            except asyncio.TimeoutError:
                continue


class WebhookDispatcherHandle:
    def __init__(self, task: asyncio.Task, stop_event: asyncio.Event) -> None:
        self.task = task
        self.stop_event = stop_event


def start_webhook_dispatcher() -> WebhookDispatcherHandle | None:
    if not WEBHOOK_URL:
        print("Webhook dispatcher not started: WEBHOOK_URL unset")
        return None

    stop_event = asyncio.Event()
    task = asyncio.create_task(_dispatch_loop(stop_event))
    return WebhookDispatcherHandle(task=task, stop_event=stop_event)


async def stop_webhook_dispatcher(handle: WebhookDispatcherHandle | None) -> None:
    if not handle:
        return
    handle.stop_event.set()
    try:
        await handle.task
    except asyncio.CancelledError:
        pass

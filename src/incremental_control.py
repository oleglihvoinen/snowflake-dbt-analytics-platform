from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable


@dataclass(frozen=True)
class Change:
    business_key: str
    updated_at: datetime
    payload_hash: str
    deleted: bool = False


@dataclass(frozen=True)
class WatermarkWindow:
    previous_high_watermark: datetime
    extraction_start: datetime
    extraction_end: datetime


def build_window(previous_high_watermark: datetime, now: datetime, lookback_minutes: int = 30) -> WatermarkWindow:
    if previous_high_watermark.tzinfo is None or now.tzinfo is None:
        raise ValueError("watermarks must be timezone-aware")
    if now < previous_high_watermark:
        raise ValueError("current time cannot be before previous watermark")
    return WatermarkWindow(
        previous_high_watermark=previous_high_watermark,
        extraction_start=previous_high_watermark - timedelta(minutes=lookback_minutes),
        extraction_end=now,
    )


def merge_changes(existing: dict[str, Change], incoming: Iterable[Change]) -> dict[str, Change]:
    """
    Deterministic last-write-wins reducer for a dbt/Snowflake incremental batch.

    Reprocessing the same batch is idempotent because identical business key,
    timestamp and payload hash do not change the resulting state.
    """
    result = dict(existing)
    for change in sorted(incoming, key=lambda c: (c.updated_at, c.business_key, c.payload_hash)):
        current = result.get(change.business_key)
        if current is None or (change.updated_at, change.payload_hash) >= (current.updated_at, current.payload_hash):
            if change.deleted:
                result.pop(change.business_key, None)
            else:
                result[change.business_key] = change
    return result


def reconcile(source: Iterable[Change], target: dict[str, Change]) -> dict[str, object]:
    source_latest = merge_changes({}, source)
    missing = sorted(set(source_latest) - set(target))
    unexpected = sorted(set(target) - set(source_latest))
    hash_mismatch = sorted(
        key for key in set(source_latest) & set(target)
        if source_latest[key].payload_hash != target[key].payload_hash
    )
    return {
        "source_count": len(source_latest),
        "target_count": len(target),
        "missing_keys": missing,
        "unexpected_keys": unexpected,
        "hash_mismatch_keys": hash_mismatch,
        "balanced": not (missing or unexpected or hash_mismatch),
    }


def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

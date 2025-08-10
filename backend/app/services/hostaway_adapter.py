from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

from ..config import DATA_DIR, HOSTAWAY_ACCOUNT_ID, HOSTAWAY_API_KEY, HOSTAWAY_API_BASE


def _slugify(value: str) -> str:
    value = value.strip().lower()
    # Replace non-alphanumeric with hyphens
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def _to_iso_utc(dt_str: str) -> str:
    # Input example: "2020-08-21 22:45:14"
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _compute_overall_rating(
    top_level: Optional[float], categories: List[Dict[str, Any]]
) -> Optional[float]:
    if top_level is not None:
        try:
            return float(top_level)
        except Exception:
            return None
    if categories:
        nums = [
            float(c.get("rating")) for c in categories if c.get("rating") is not None
        ]
        if nums:
            return round(sum(nums) / len(nums), 2)
    return None


def _category_map(categories: List[Dict[str, Any]]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for c in categories or []:
        name = c.get("category") or "unknown"
        rating = c.get("rating")
        if rating is None:
            continue
        out[str(name)] = float(rating)
    return out


def _normalize_type(raw_type: Optional[str]) -> str:
    if not raw_type:
        return "unknown"
    return raw_type.replace("-", "_")


def load_hostaway_reviews(
    approvals_map: Optional[Dict[str, bool]] = None,
) -> List[Dict[str, Any]]:
    """Load mocked Hostaway reviews and normalize them for the frontend.

    approvals_map: optional mapping of review_id -> approved flag to enrich results.
    """
    approvals_map = approvals_map or {}
    mock_path: Path = DATA_DIR / "hostaway_mock.json"
    with mock_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    items = raw.get("result", [])
    return normalize_hostaway_items(items, approvals_map)


def fetch_hostaway_live_reviews() -> List[Dict[str, Any]]:
    """Fetch reviews from Hostaway API (sandbox/production depending on keys).

    Returns Hostaway raw payload list under result[], or empty list on errors.
    """
    if not HOSTAWAY_API_KEY or not HOSTAWAY_ACCOUNT_ID:
        return []

    url = f"{HOSTAWAY_API_BASE}/accounts/{HOSTAWAY_ACCOUNT_ID}/reviews"
    headers = {
        "Authorization": f"Bearer {HOSTAWAY_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            return []
        data = resp.json()
        return data.get("result", []) or []
    except Exception:
        return []


def normalize_hostaway_items(
    items: List[Dict[str, Any]], approvals_map: Optional[Dict[str, bool]] = None
) -> List[Dict[str, Any]]:
    approvals_map = approvals_map or {}
    normalized: List[Dict[str, Any]] = []
    for item in items:
        review_id = str(item.get("id"))
        listing_name = item.get("listingName") or "Unknown Listing"
        listing_id = f"hostaway:{_slugify(listing_name)}"
        categories = item.get("reviewCategory") or []
        rating_overall = _compute_overall_rating(item.get("rating"), categories)
        normalized.append(
            {
                "review_id": review_id,
                "listing_id": listing_id,
                "listing_name": listing_name,
                "channel": "hostaway",
                "type": _normalize_type(item.get("type")),
                "status": item.get("status") or "unknown",
                "rating_overall": rating_overall,
                "category_ratings": _category_map(categories),
                "text_public": item.get("publicReview"),
                "submitted_at": _to_iso_utc(item.get("submittedAt")),
                "author_name": item.get("guestName") or None,
                "approved": bool(approvals_map.get(review_id, False)),
            }
        )

    normalized.sort(key=lambda r: r.get("submitted_at", ""), reverse=True)
    return normalized

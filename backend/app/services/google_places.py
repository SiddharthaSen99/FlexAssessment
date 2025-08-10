from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from ..config import GOOGLE_PLACES_API_KEY


PLACES_FIND_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def _to_iso_from_unix(ts: Optional[int]) -> str:
    if ts is None:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return (
        datetime.fromtimestamp(int(ts), tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def find_place_id_by_text(query: str) -> Optional[str]:
    if not GOOGLE_PLACES_API_KEY:
        return None
    params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id,name",
        "key": GOOGLE_PLACES_API_KEY,
    }
    try:
        resp = requests.get(PLACES_FIND_URL, params=params, timeout=15)
        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            return None
        return candidates[0].get("place_id")
    except Exception:
        return None


def fetch_place_details(place_id: str) -> Dict[str, Any]:
    if not GOOGLE_PLACES_API_KEY:
        return {}
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,reviews",
        "key": GOOGLE_PLACES_API_KEY,
    }
    try:
        resp = requests.get(PLACES_DETAILS_URL, params=params, timeout=20)
        return resp.json().get("result", {})
    except Exception:
        return {}


def normalize_google_reviews(
    place: Dict[str, Any],
    approvals_map: Optional[Dict[str, bool]] = None,
    listing_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    approvals_map = approvals_map or {}
    place_id = place.get("place_id") or "unknown"
    listing_name = place.get("name") or "Google Place"
    reviews = place.get("reviews") or []
    normalized: List[Dict[str, Any]] = []
    for r in reviews:
        rid = f"{place_id}:{r.get('time')}"
        normalized.append(
            {
                "review_id": rid,
                "listing_id": listing_id or f"google:{place_id}",
                "listing_name": listing_name,
                "channel": "google",
                "type": "guest_to_host",
                "status": "published",
                "rating_overall": float(r.get("rating") or 0) * 2.0,
                "category_ratings": {},
                "text_public": r.get("text") or r.get("original_text", {}).get("text"),
                "submitted_at": _to_iso_from_unix(r.get("time")),
                "author_name": r.get("author_name"),
                "approved": bool(approvals_map.get(rid, False)),
            }
        )
    # newest first by time
    normalized.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
    return normalized

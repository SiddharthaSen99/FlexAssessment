from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query

from ..models.db import SessionLocal
from ..models.approvals import upsert_approval, get_approvals_map
from ..schemas.reviews import ApproveRequest
from ..services.hostaway_adapter import (
    load_hostaway_reviews,
    fetch_hostaway_live_reviews,
    normalize_hostaway_items,
)
from ..config import HOSTAWAY_LIVE_MODE
from ..services.google_places import (
    find_place_id_by_text,
    fetch_place_details,
    normalize_google_reviews,
)


router = APIRouter()


@router.get("/reviews/hostaway")
def get_hostaway_reviews(
    listingId: Optional[str] = Query(default=None),
    startDate: Optional[str] = Query(default=None),
    endDate: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),  # host_to_guest | guest_to_host
    status: Optional[str] = Query(default=None),
    minRating: Optional[float] = Query(default=None),
    approved: Optional[bool] = Query(default=None),
    source: Optional[str] = Query(default=None, description="mock|live|auto"),
) -> Dict[str, Any]:
    """Return normalized Hostaway reviews with optional server-side filtering."""
    session = SessionLocal()
    try:
        approvals = get_approvals_map(session)
        use_source = (source or ("live" if HOSTAWAY_LIVE_MODE else "auto")).lower()

        if use_source == "mock":
            reviews = load_hostaway_reviews(approvals)
        elif use_source == "live":
            live_items = fetch_hostaway_live_reviews()
            # If empty (sandbox), return empty normalized list
            reviews = normalize_hostaway_items(live_items, approvals)
        else:  # auto: try live, fall back to mock if empty
            live_items = fetch_hostaway_live_reviews()
            if live_items:
                reviews = normalize_hostaway_items(live_items, approvals)
            else:
                reviews = load_hostaway_reviews(approvals)

        def parse_iso(date_str: Optional[str]) -> Optional[datetime]:
            if not date_str:
                return None
            try:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except Exception:
                return None

        start_dt = parse_iso(startDate)
        end_dt = parse_iso(endDate)

        filtered: List[Dict[str, Any]] = []
        for r in reviews:
            if listingId and r["listing_id"] != listingId:
                continue
            if type and r["type"] != type:
                continue
            if status and r["status"] != status:
                continue
            if minRating is not None:
                if r["rating_overall"] is None or r["rating_overall"] < float(
                    minRating
                ):
                    continue
            if approved is not None and r.get("approved") is not None:
                if bool(r["approved"]) != bool(approved):
                    continue

            # Date filtering
            if start_dt or end_dt:
                r_dt = parse_iso(r.get("submitted_at"))
                if r_dt is None:
                    continue
                if start_dt and r_dt < start_dt:
                    continue
                if end_dt and r_dt > end_dt:
                    continue

            filtered.append(r)

        return {"status": "success", "result": filtered}
    finally:
        session.close()


@router.get("/reviews/google")
def get_google_reviews(
    query: Optional[str] = Query(
        default=None, description="Text to find the place (e.g., property name + city)"
    ),
    placeId: Optional[str] = Query(default=None),
    listingId: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    session = SessionLocal()
    try:
        approvals = get_approvals_map(session)
        pid = placeId or (find_place_id_by_text(query) if query else None)
        if not pid:
            return {"status": "success", "result": []}
        place = fetch_place_details(pid)
        # ensure place_id in result for stable IDs
        if place and not place.get("place_id"):
            place["place_id"] = pid
        normalized = normalize_google_reviews(
            place, approvals_map=approvals, listing_id=listingId
        )
        return {"status": "success", "result": normalized}
    finally:
        session.close()


@router.post("/reviews/approve")
def approve_review(payload: ApproveRequest) -> Dict[str, Any]:
    session = SessionLocal()
    try:
        upsert_approval(
            session=session,
            review_id=str(payload.review_id),
            approved=bool(payload.approved),
            channel=payload.channel or "hostaway",
            listing_id=payload.listing_id,
        )
        return {"status": "success"}
    finally:
        session.close()


@router.get("/reviews/selected")
def get_selected_reviews(
    listingId: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None, description="mock|live|auto"),
) -> Dict[str, Any]:
    session = SessionLocal()
    try:
        approvals = get_approvals_map(session)
        use_source = (source or ("live" if HOSTAWAY_LIVE_MODE else "auto")).lower()

        if use_source == "mock":
            reviews = load_hostaway_reviews(approvals)
        elif use_source == "live":
            live_items = fetch_hostaway_live_reviews()
            reviews = normalize_hostaway_items(live_items, approvals)
        else:
            live_items = fetch_hostaway_live_reviews()
            if live_items:
                reviews = normalize_hostaway_items(live_items, approvals)
            else:
                reviews = load_hostaway_reviews(approvals)
        selected = [r for r in reviews if r.get("approved")]
        if listingId:
            selected = [r for r in selected if r["listing_id"] == listingId]
        return {"status": "success", "result": selected}
    finally:
        session.close()

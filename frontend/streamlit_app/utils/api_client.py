import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def api_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    resp = requests.get(url, params=params or {}, timeout=20)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    resp = requests.post(url, json=json_body, timeout=20)
    resp.raise_for_status()
    return resp.json()


def get_reviews(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return api_get("/api/reviews/hostaway", params=params)


def approve_review(
    review_id: str,
    approved: bool,
    channel: str = "hostaway",
    listing_id: Optional[str] = None,
) -> Dict[str, Any]:
    return api_post(
        "/api/reviews/approve",
        {
            "review_id": review_id,
            "approved": approved,
            "channel": channel,
            "listing_id": listing_id,
        },
    )


def get_selected_reviews(
    listing_id: Optional[str] = None, source: Optional[str] = None
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if listing_id:
        params["listingId"] = listing_id
    if source:
        params["source"] = source
    return api_get("/api/reviews/selected", params=params)


def get_google_reviews(
    query: Optional[str] = None,
    place_id: Optional[str] = None,
    listing_id: Optional[str] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if query:
        params["query"] = query
    if place_id:
        params["placeId"] = place_id
    if listing_id:
        params["listingId"] = listing_id
    return api_get("/api/reviews/google", params=params)

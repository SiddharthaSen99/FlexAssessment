from typing import Dict, Optional

from pydantic import BaseModel, Field


class NormalizedReview(BaseModel):
    review_id: str
    listing_id: str
    listing_name: str
    channel: str
    type: str
    status: str
    rating_overall: Optional[float] = None
    category_ratings: Dict[str, float] = Field(default_factory=dict)
    text_public: Optional[str] = None
    submitted_at: str
    author_name: Optional[str] = None
    approved: bool = False


class ApproveRequest(BaseModel):
    review_id: str
    approved: bool
    channel: Optional[str] = "hostaway"
    listing_id: Optional[str] = None

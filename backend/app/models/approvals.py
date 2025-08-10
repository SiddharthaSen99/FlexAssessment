from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .db import Base


class Approval(Base):
    __tablename__ = "approvals"

    review_id = Column(String, primary_key=True)
    approved = Column(Boolean, nullable=False, default=False)
    channel = Column(String, nullable=False, default="hostaway")
    listing_id = Column(String, nullable=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


def upsert_approval(
    session: Session,
    *,
    review_id: str,
    approved: bool,
    channel: str = "hostaway",
    listing_id: Optional[str] = None,
) -> None:
    obj = session.get(Approval, review_id)
    if obj is None:
        obj = Approval(review_id=review_id)
        session.add(obj)
    obj.approved = bool(approved)
    obj.channel = channel
    obj.listing_id = listing_id
    session.commit()


def get_approvals_map(session: Session) -> Dict[str, bool]:
    rows = session.query(Approval).all()
    return {str(r.review_id): bool(r.approved) for r in rows}

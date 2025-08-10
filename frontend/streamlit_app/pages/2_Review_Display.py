from typing import Dict, List

import pandas as pd
import streamlit as st

from utils.api_client import get_reviews, get_selected_reviews
from utils.theme import inject_theme, render_stars


st.set_page_config(page_title="Property Reviews", layout="wide")
st.title("Property Reviews (Public Preview)")
inject_theme()

# Light section styles inspired by Flex property page
st.markdown(
    """
    <style>
      .flx-hero { margin-bottom: 24px; }
      .rev-container { max-width: 820px; margin: 0 auto; }
      .rev-section { background: #f2f4f1; border-radius: 12px; padding: 24px; border: 1px solid #e0e5de; }
      .rev-header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 18px; }
      .rev-title { font-size: 22px; font-weight: 700; color: #1f2937; margin: 0; }
      .rev-summary { display:flex; gap:12px; align-items:center; }
      .rev-avg-box { background: white; border: 1px solid #e6e6e6; border-radius: 10px; padding: 10px 12px; display:flex; gap:10px; align-items:center; }
      .rev-avg-num { font-size: 24px; font-weight: 700; color: #111827; line-height: 1; }
      .rev-count { color: #6b7280; font-size: 12px; }
      .rev-grid { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 18px; margin-top: 24px; }
      @media (max-width: 1100px) { .rev-grid { grid-template-columns: 1fr; } }
      .rev-card { background:#fbfaf5; border:1px solid #e2e2da; border-radius:12px; padding:16px; }
      .rev-card-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
      .rev-meta { color:#6b7280; font-size:12px; }
      .rev-rating { background:#ffffff; border:1px solid #e5e7eb; color:#111827; border-radius:999px; padding:4px 8px; font-size:12px; font-weight:700; }
      .rev-text { color:#111827; font-size:15px; line-height:1.6; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    source = st.selectbox(
        "Data source",
        options=["auto", "mock", "live"],
        index=0,
        help="Use 'mock' for provided JSON; 'live' if Hostaway credentials are set",
    )
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()


@st.cache_data(ttl=60)
def all_listings(src: str) -> List[Dict]:
    res = get_reviews({"source": src})
    rows = res.get("result", [])
    # Build unique listing list
    seen = {}
    for r in rows:
        seen[r["listing_id"]] = r["listing_name"]
    return [{"listing_id": k, "listing_name": v} for k, v in seen.items()]


listings = all_listings(source)
if not listings:
    st.info("No listings found.")
    st.stop()

listing_display = {
    f"{x['listing_name']} ({x['listing_id']})": x["listing_id"] for x in listings
}
choice = st.selectbox("Select a listing", options=list(listing_display.keys()))
selected_listing_id = listing_display[choice]

data = get_selected_reviews(selected_listing_id, source)
rows = data.get("result", [])
if not rows:
    # Try fetching via the main reviews endpoint with approved=true using the same source
    data = get_reviews(
        {"source": source, "listingId": selected_listing_id, "approved": True}
    )
    rows = data.get("result", [])

if not rows:
    st.warning("No approved reviews yet for this listing.")
    st.stop()

# Header / hero
hero_title = next(
    (l["listing_name"] for l in listings if l["listing_id"] == selected_listing_id),
    "Selected property",
)
st.markdown(
    f"<div class='flx-hero'><div><div class='flx-title'>{hero_title}</div><div class='flx-subtitle'>Guest reviews curated by Flex Living</div><div class='flx-summary'><span class='flx-badge'>Approved: {len(rows)}</span></div></div></div>",
    unsafe_allow_html=True,
)

avg = (
    sum([r.get("rating_overall") or 0 for r in rows])
    / max(1, len([r for r in rows if r.get("rating_overall") is not None]))
    if rows
    else 0
)
st.markdown(
    f"""
    <div class='rev-container'>
      <div class='rev-section'>
        <div class='rev-header'>
          <div class='rev-title'>Guest reviews</div>
          <div class='rev-summary'>
            <div class='rev-avg-box'><div class='rev-avg-num'>{avg:.1f}</div></div>
            <div class='rev-count'>{len(rows)} approved</div>
          </div>
        </div>
        <div class='rev-grid'>
    """,
    unsafe_allow_html=True,
)

cards_html = []
for r in rows:
    date = (r.get("submitted_at") or "")[:10]
    author = r.get("author_name") or "Guest"
    text = (r.get("text_public") or "").replace("<", "&lt;").replace(">", "&gt;")
    rating = r.get("rating_overall")
    rating_chip = (
        f"<span class='rev-rating'>{rating:.1f}</span>" if rating is not None else ""
    )
    cards_html.append(
        f"<div class='rev-card'><div class='rev-card-head'><div class='rev-meta'>{author} • {date}</div>{rating_chip}</div><div class='rev-text'>{text}</div></div>"
    )
st.markdown("\n".join(cards_html), unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

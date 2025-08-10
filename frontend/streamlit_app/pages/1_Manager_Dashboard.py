import datetime as dt
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from utils.api_client import approve_review, get_reviews, get_google_reviews
from utils.theme import render_kpi, render_badge


st.set_page_config(page_title="Manager Dashboard", layout="wide")
st.title("Manager Dashboard")


@st.cache_data(ttl=60)
def fetch_reviews(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = get_reviews(params)
    return data.get("result", [])


with st.sidebar:
    st.header("Filters")
    today = dt.date.today()
    start_date = st.date_input("Start date", value=today - dt.timedelta(days=365))
    end_date = st.date_input("End date", value=today)
    min_rating = st.slider("Min rating", 0.0, 10.0, 0.0, step=0.5)
    review_type = st.selectbox(
        "Type", options=["All", "guest_to_host", "host_to_guest"], index=0
    )
    status = st.selectbox("Status", options=["All", "published"], index=0)
    source = st.selectbox(
        "Data source",
        options=["auto", "mock", "live"],
        index=0,
        help="Use 'mock' for provided JSON; 'live' if you have Hostaway API credentials",
    )

params = {
    "startDate": dt.datetime.combine(start_date, dt.time.min).isoformat() + "Z",
    "endDate": dt.datetime.combine(end_date, dt.time.max).isoformat() + "Z",
    "minRating": min_rating,
    "source": source,
}
if review_type != "All":
    params["type"] = review_type
if status != "All":
    params["status"] = status

reviews = fetch_reviews(params)
df = pd.DataFrame(reviews)

if df.empty:
    st.info("No reviews match the current filters. Adjust filters to see results.")
    listings: List[str] = []
else:
    listings = (
        sorted(df["listing_name"].dropna().unique().tolist())
        if "listing_name" in df.columns
        else []
    )

with st.sidebar:
    selected_listings = st.multiselect(
        "Listings", options=listings, default=listings if listings else []
    )

if selected_listings and not df.empty and "listing_name" in df.columns:
    df = df[df["listing_name"].isin(selected_listings)]

if not df.empty:
    # KPI cards (styled)
    kpi_html = (
        "<div class='flx-kpi-grid'>"
        + render_kpi("Reviews", str(len(df)))
        + render_kpi("Average rating", f"{df['rating_overall'].dropna().mean():.2f}")
        + render_kpi("Approved", str(int(df["approved"].sum())))
        + "</div>"
    )
    st.markdown(kpi_html, unsafe_allow_html=True)

if not df.empty:
    st.markdown(
        "### Reviews " + render_badge("filtered", "secondary"), unsafe_allow_html=True
    )

    display_cols = [
        "submitted_at",
        "listing_name",
        "author_name",
        "rating_overall",
        "type",
        "status",
        "text_public",
        "approved",
        "review_id",
    ]
    show_df = df[display_cols].rename(
        columns={
            "submitted_at": "Date",
            "listing_name": "Listing",
            "author_name": "Guest",
            "rating_overall": "Rating",
            "type": "Type",
            "status": "Status",
            "text_public": "Review",
            "approved": "Approved",
            "review_id": "ID",
        }
    )
    st.dataframe(show_df, hide_index=True, use_container_width=True)

if not df.empty:
    st.divider()
    st.subheader("Approval actions")
    ids = df["review_id"].astype(str).tolist()
    selected_ids = st.multiselect("Select review IDs", options=ids)
    col_a, col_b = st.columns(2)
    with col_a:
        if (
            st.button("Approve selected", type="primary", key="approve_selected_btn")
            and selected_ids
        ):
            for rid in selected_ids:
                row = df[df["review_id"].astype(str) == rid].iloc[0]
                approve_review(review_id=str(rid), approved=True, channel="hostaway", listing_id=row["listing_id"])  # type: ignore
            st.success(f"Approved {len(selected_ids)} review(s)")
            st.cache_data.clear()
            st.rerun()
    with col_b:
        if (
            st.button("Unapprove selected", key="unapprove_selected_btn")
            and selected_ids
        ):
            for rid in selected_ids:
                row = df[df["review_id"].astype(str) == rid].iloc[0]
                approve_review(review_id=str(rid), approved=False, channel="hostaway", listing_id=row["listing_id"])  # type: ignore
            st.success(f"Unapproved {len(selected_ids)} review(s)")
            st.cache_data.clear()
            st.rerun()

st.divider()
st.subheader("Google Reviews (exploration)")
col1, col2 = st.columns([2, 1])
with col1:
    google_query = st.text_input(
        "Find place by text (property name + city)",
        placeholder="e.g., 29 Shoreditch Heights London",
    )
with col2:
    target_listing = st.selectbox(
        "Attach to listing (optional)",
        options=["None"] + listings if listings else ["None"],
        index=0,
    )

if st.button("Load Google reviews", key="load_google_reviews_btn") and google_query:
    listing_choice = None if target_listing == "None" else target_listing
    resp = get_google_reviews(query=google_query, listing_id=None)
    gres = resp.get("result", [])
    if not gres:
        st.info(
            "No Google reviews found (check API key/quota or try a different query)."
        )
    else:
        gdf = pd.DataFrame(gres)
        st.dataframe(
            gdf[
                [
                    "submitted_at",
                    "author_name",
                    "rating_overall",
                    "text_public",
                    "listing_name",
                ]
            ].rename(
                columns={
                    "submitted_at": "Date",
                    "author_name": "Author",
                    "rating_overall": "Rating",
                    "text_public": "Review",
                    "listing_name": "Place",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

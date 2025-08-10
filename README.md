## Flex Living – Reviews Dashboard (Assessment)

### Tech stack

- Backend: FastAPI, Pydantic, SQLAlchemy (SQLite)
- Frontend: Streamlit, Pandas, Altair
- Hosting: Railway(backend), Vercel (frontend) https://flex-assessment.vercel.app/

### What’s included

- Mocked Hostaway Reviews integration with a normalized schema
- Required API route: GET `/api/reviews/hostaway` (filterable)
- Approvals persistence (SQLite): POST `/api/reviews/approve`, GET `/api/reviews/selected`
- Manager Dashboard (filters, KPIs, approvals)
- Property Review Display (public preview) using only approved reviews
- Optional live Hostaway fetch (sandbox likely empty) and Google Reviews exploration via Places API

## Local setup and running

### 1) Create a virtual environment and install dependencies

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows cmd
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2) Configure environment variables

The app reads a `.env` file at the project root. Alternatively, set variables in your terminal session.

Recommended `.env` (root):

```
HOSTAWAY_ACCOUNT_ID=61148
HOSTAWAY_API_KEY=
HOSTAWAY_LIVE_MODE=false
HOSTAWAY_API_BASE=https://api.hostaway.com/v1
GOOGLE_PLACES_API_KEY=
API_BASE_URL=http://localhost:8000
```

Windows cmd (if not using .env):

```bat
set API_BASE_URL=http://localhost:8000
set HOSTAWAY_ACCOUNT_ID=61148
set HOSTAWAY_API_KEY=YOUR_HOSTAWAY_KEY
set HOSTAWAY_LIVE_MODE=false
set GOOGLE_PLACES_API_KEY=YOUR_GOOGLE_KEY
```

PowerShell:

```powershell
$env:API_BASE_URL="http://localhost:8000"
$env:HOSTAWAY_ACCOUNT_ID="61148"
$env:HOSTAWAY_API_KEY="YOUR_HOSTAWAY_KEY"
$env:HOSTAWAY_LIVE_MODE="false"
$env:GOOGLE_PLACES_API_KEY="YOUR_GOOGLE_KEY"
```

### 3) Run the backend API

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 4) Run the Streamlit app (separate terminal) – optional

```bash
streamlit run frontend/streamlit_app/Home.py
```

If Streamlit shows a Windows file watcher error, use polling:

```bat
set STREAMLIT_SERVER_FILE_WATCHER_TYPE=poll
streamlit run frontend/streamlit_app/Home.py
```

## Using the app

### Manager Dashboard

- Choose Data source: `auto` (try live then mock), `mock` (provided JSON), or `live` (uses Hostaway keys)
- Filter by date, rating, type, status, and listing
- Approve/unapprove reviews; changes persist to SQLite

### Property Review Display

- Select a listing to view only approved reviews in a property-style layout

### Next.js frontend (alternative UI)

There is a modern Next.js frontend with Tailwind under `frontend_next/`.

Run it in a separate terminal:

```bash
cd frontend_next
npm i
# Windows cmd
set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
# PowerShell
# $env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"; npm run dev
```

Pages

- `/` Home
- `/dashboard` Manager Dashboard (filters, KPIs, approvals)
- `/property` Property reviews (approved only, public-style layout)
- `/google` Google Reviews (exploration)

If you see TypeScript/path issues on Windows, clear the Next cache by deleting the `.next` folder and re-run `npm run dev`.

### Google Reviews (exploration)

- Requires `GOOGLE_PLACES_API_KEY` and the “Places API” enabled in your GCP project
- Enter a place query (e.g., “Property name, City”) and load recent text reviews (up to ~5)
  - Note: Google policies often restrict storing review text long-term; treat as an exploration

## API behavior

### GET `/api/reviews/hostaway`

Returns normalized Hostaway reviews.

- Query params: `listingId`, `startDate`, `endDate`, `type`, `status`, `minRating`, `approved`, `source` (mock|live|auto)
- Response: `{ "status": "success", "result": [NormalizedReview...] }`

Example (Windows cmd):

```bat
curl "http://localhost:8000/api/reviews/hostaway?minRating=8&source=mock"
```

### POST `/api/reviews/approve`

Persist approval state (SQLite). Body:

```json
{
  "review_id": "1001",
  "approved": true,
  "channel": "hostaway",
  "listing_id": "hostaway:2b-n1-a-29-shoreditch-heights"
}
```

### GET `/api/reviews/selected`

Only approved reviews (optionally filter by `listingId`; supports `source` like above).

### GET `/api/reviews/google`

Fetch and normalize Google Place reviews.

- Query params: `query` (text) or `placeId`, optional `listingId` to tag
- Response: same normalized schema with `channel: "google"`

## Normalization rules

- `review_id`: source id as string
- `listing_id`: stable slug (e.g., `hostaway:{slug(listingName)}`)
- `listing_name`: name from the source
- `channel`: `hostaway` or `google`
- `type`: `guest_to_host` or `host_to_guest`
- `status`: published or source-provided
- `rating_overall`: top-level rating; if missing, average of category ratings
- `category_ratings`: flattened map of category → number
- `text_public`: review text
- `submitted_at`: ISO 8601 UTC (e.g., `2024-06-15T10:24:10Z`)
- `approved`: boolean from SQLite approvals table

## Key design and logic decisions

### Architecture

- Separate FastAPI backend for data normalization and persistence
- Streamlit frontend for rapid, clean dashboarding and a property-style review display

### UX choices

- Minimal, modern dark theme with accent color and card-based layout
- Fixed sidebar filters and styled KPI cards for quick portfolio overview
- Clear Approve/Unapprove actions and a public preview mirroring a property page section

### Live vs mock data

- `source=mock|live|auto` keeps the UI fast and testable while allowing a live switch
- Sandbox Hostaway commonly returns zero reviews; `auto` falls back to mock

### Persistence

- SQLite stores only approvals (`approvals` table). All other metrics computed on the fly

## Google Reviews findings

- Google Places Details typically returns up to ~5 text reviews per place along with summary metrics
- API key configuration matters: enable billing, enable "Places API", ensure no restrictive referrer rules for server-side calls
- Terms often restrict storing user review text; consider aggregations or linking when going to production

## Notes

- Mock data lives in `backend/data/hostaway_mock.json`
- SQLite DB is created at `backend/app/app.db` on first run
- If you change environment variables, restart the backend process

## Environment variables quick reference

Backend (.env or set per terminal):

```
HOSTAWAY_ACCOUNT_ID=61148
HOSTAWAY_API_KEY=
HOSTAWAY_LIVE_MODE=false
HOSTAWAY_API_BASE=https://api.hostaway.com/v1
GOOGLE_PLACES_API_KEY=
API_BASE_URL=http://localhost:8000
```

Windows cmd (backend terminal):

```
set HOSTAWAY_ACCOUNT_ID=61148
set HOSTAWAY_API_KEY=YOUR_HOSTAWAY_KEY
set HOSTAWAY_LIVE_MODE=false
set GOOGLE_PLACES_API_KEY=YOUR_GOOGLE_KEY
uvicorn backend.app.main:app --reload --port 8000
```

PowerShell (backend terminal):

```
$env:HOSTAWAY_ACCOUNT_ID="61148"
$env:HOSTAWAY_API_KEY="YOUR_HOSTAWAY_KEY"
$env:HOSTAWAY_LIVE_MODE="false"
$env:GOOGLE_PLACES_API_KEY="YOUR_GOOGLE_KEY"
uvicorn backend.app.main:app --reload --port 8000
```

Next.js frontend (if `.env.local` not used):

```
cd frontend_next
set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # Windows cmd
npm run dev
# PowerShell: $env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"; npm run dev
```
The backend is hosted on Railway while the frontend is live on https://flex-assessment.vercel.app/

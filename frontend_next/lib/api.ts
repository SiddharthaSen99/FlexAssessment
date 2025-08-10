export type NormalizedReview = {
  review_id: string
  listing_id: string
  listing_name: string
  channel: string
  type: string
  status: string
  rating_overall: number | null
  category_ratings: Record<string, number>
  text_public: string | null
  submitted_at: string
  author_name: string | null
  approved: boolean
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    cache: 'no-store',
  })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export async function getReviews(params: Record<string, string | number | boolean> = {}) {
  const query = new URLSearchParams(params as Record<string, string>)
  return http<{ status: string; result: NormalizedReview[] }>(`/api/reviews/hostaway?${query.toString()}`)
}

export async function approveReview(review_id: string, approved: boolean, listing_id?: string) {
  return http(`/api/reviews/approve`, {
    method: 'POST',
    body: JSON.stringify({ review_id, approved, channel: 'hostaway', listing_id }),
  })
}

export async function getSelected(listingId?: string, source?: string) {
  const query = new URLSearchParams()
  if (listingId) query.set('listingId', listingId)
  if (source) query.set('source', source)
  return http<{ status: string; result: NormalizedReview[] }>(`/api/reviews/selected?${query.toString()}`)
}

export async function getGoogleReviews(params: { query?: string; placeId?: string; listingId?: string }) {
  const query = new URLSearchParams()
  if (params.query) query.set('query', params.query)
  if (params.placeId) query.set('placeId', params.placeId)
  if (params.listingId) query.set('listingId', params.listingId)
  return http<{ status: string; result: NormalizedReview[] }>(`/api/reviews/google?${query.toString()}`)
}



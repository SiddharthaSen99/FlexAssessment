"use client"
import { useState } from 'react'
import { getGoogleReviews } from '@/lib/api'

export default function GoogleReviewsPage() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [rows, setRows] = useState<any[]>([])

  async function run() {
    setLoading(true)
    const res = await getGoogleReviews({ query })
    setRows(res.result || [])
    setLoading(false)
  }

  return (
    <main className="container-narrow py-8 space-y-6">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold">Google Reviews (exploration)</h1>
          <p className="text-neutral-300 mt-1">Requires GOOGLE_PLACES_API_KEY set in the backend.</p>
        </div>
      </div>

      <div className="flex gap-2">
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Property name + city"
               className="card px-3 py-2 flex-1" />
        <button onClick={run} className="px-4 py-2 rounded bg-brand-accent text-black font-semibold">Load</button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-900">
            <tr>
              <th className="text-left p-3">Date</th>
              <th className="text-left p-3">Author</th>
              <th className="text-left p-3">Rating</th>
              <th className="text-left p-3">Text</th>
              <th className="text-left p-3">Place</th>
            </tr>
          </thead>
          <tbody>
            {loading && (<tr><td className="p-4" colSpan={5}>Loading…</td></tr>)}
            {!loading && rows.map((r) => (
              <tr key={r.review_id} className="odd:bg-neutral-900/40">
                <td className="p-3">{(r.submitted_at || '').slice(0,10)}</td>
                <td className="p-3">{r.author_name || 'Guest'}</td>
                <td className="p-3">{r.rating_overall ?? '-'}</td>
                <td className="p-3">{r.text_public}</td>
                <td className="p-3">{r.listing_name}</td>
              </tr>
            ))}
            {!loading && !rows.length && (<tr><td className="p-4" colSpan={5}>No results</td></tr>)}
          </tbody>
        </table>
      </div>
    </main>
  )
}



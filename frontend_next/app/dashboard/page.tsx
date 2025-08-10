"use client"
import { useEffect, useMemo, useState } from 'react'
import { approveReview, getReviews, type NormalizedReview } from '@/lib/api'

export default function DashboardPage() {
  const [rows, setRows] = useState<NormalizedReview[]>([])
  const [loading, setLoading] = useState(true)
  const [source, setSource] = useState<'auto' | 'mock' | 'live'>('auto')
  const [minRating, setMinRating] = useState(0)

  useEffect(() => {
    const run = async () => {
      setLoading(true)
      const res = await getReviews({ source, minRating })
      setRows(res.result)
      setLoading(false)
    }
    run()
  }, [source, minRating])

  const avg = useMemo(() => {
    const nums = rows.map(r => r.rating_overall).filter((n): n is number => n != null)
    if (!nums.length) return 0
    return +(nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(2)
  }, [rows])

  return (
    <main className="container-narrow py-8 space-y-6">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold">Manager Dashboard</h1>
          <p className="text-neutral-300 mt-1">Filter, inspect, and approve reviews.</p>
        </div>
        <div className="flex gap-2">
          <select value={source} onChange={e => setSource(e.target.value as any)} className="card px-3 py-2">
            <option value="auto">auto</option>
            <option value="mock">mock</option>
            <option value="live">live</option>
          </select>
          <div className="card px-3 py-2 flex items-center gap-2">
            <label htmlFor="minRating" className="text-neutral-300 text-sm">Filter by rating ≥</label>
            <input id="minRating" type="number" min={0} max={10} step={0.5} value={minRating}
                   onChange={e => setMinRating(Number(e.target.value))}
                   className="bg-transparent outline-none w-16" />
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-3">
        <div className="card p-4"><div className="text-neutral-400 text-sm">Reviews</div><div className="text-2xl font-bold">{rows.length}</div></div>
        <div className="card p-4"><div className="text-neutral-400 text-sm">Average rating</div><div className="text-2xl font-bold">{avg}</div></div>
        <div className="card p-4"><div className="text-neutral-400 text-sm">Approved</div><div className="text-2xl font-bold">{rows.filter(r => r.approved).length}</div></div>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-900">
            <tr>
              <th className="text-left p-3">Date</th>
              <th className="text-left p-3">Listing</th>
              <th className="text-left p-3">Guest</th>
              <th className="text-left p-3">Rating</th>
              <th className="text-left p-3">Approved</th>
              <th className="text-left p-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td className="p-4" colSpan={6}>Loading…</td></tr>
            )}
            {!loading && rows.map(r => (
              <tr key={r.review_id} className="odd:bg-neutral-900/40">
                <td className="p-3">{r.submitted_at.slice(0,10)}</td>
                <td className="p-3">{r.listing_name}</td>
                <td className="p-3">{r.author_name || 'Guest'}</td>
                <td className="p-3">{r.rating_overall ?? '-'}</td>
                <td className="p-3">{r.approved ? 'Yes' : 'No'}</td>
                <td className="p-3">
                  <button onClick={async () => {
                    await approveReview(r.review_id, !r.approved, r.listing_id)
                    setRows(prev => prev.map(x => x.review_id === r.review_id ? { ...x, approved: !x.approved } : x))
                  }} className="px-3 py-1 rounded bg-brand-accent text-black font-semibold">
                    {r.approved ? 'Unapprove' : 'Approve'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  )
}



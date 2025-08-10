"use client"
import { useEffect, useMemo, useState } from 'react'
import { getReviews, getSelected, type NormalizedReview } from '@/lib/api'

export default function PropertyPage() {
  const [source, setSource] = useState<'auto' | 'mock' | 'live'>('auto')
  const [listings, setListings] = useState<{ id: string; name: string }[]>([])
  const [listingId, setListingId] = useState<string>('')
  const [rows, setRows] = useState<NormalizedReview[]>([])

  useEffect(() => {
    const run = async () => {
      const res = await getReviews({ source })
      const seen = new Map<string, string>()
      res.result.forEach(r => seen.set(r.listing_id, r.listing_name))
      const arr = Array.from(seen.entries()).map(([id, name]) => ({ id, name }))
      setListings(arr)
      if (arr.length && !listingId) setListingId(arr[0].id)
    }
    run()
  }, [source])

  useEffect(() => {
    const run = async () => {
      if (!listingId) return
      const sel = await getSelected(listingId, source)
      let data = sel.result
      if (!data.length) {
        const alt = await getReviews({ source, listingId, approved: true })
        data = alt.result
      }
      setRows(data)
    }
    run()
  }, [listingId, source])

  const avg = useMemo(() => {
    const nums = rows.map(r => r.rating_overall).filter((n): n is number => n != null)
    if (!nums.length) return 0
    return +(nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(1)
  }, [rows])

  return (
    <main className="container-narrow py-8 space-y-6">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold">Property Reviews</h1>
          <p className="text-neutral-300 mt-1">Approved reviews only.</p>
        </div>
        <div className="flex gap-2">
          <select value={source} onChange={e => setSource(e.target.value as any)} className="card px-3 py-2">
            <option value="auto">auto</option>
            <option value="mock">mock</option>
            <option value="live">live</option>
          </select>
          <select value={listingId} onChange={e => setListingId(e.target.value)} className="card px-3 py-2">
            {listings.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        </div>
      </div>

      <section className="bg-gradient-to-br from-brand-accent/20 to-transparent rounded-xl border border-neutral-800 p-6">
        <h2 className="text-2xl font-semibold">{listings.find(l => l.id === listingId)?.name || 'Selected property'}</h2>
        <div className="text-neutral-300 mt-1">Guest reviews curated by Flex Living</div>
        <div className="mt-3 inline-flex items-center gap-3 bg-brand-card border border-neutral-800 rounded-full px-4 py-2">
          <div className="text-2xl font-bold">{avg}</div>
          <div className="text-neutral-300 text-sm">{rows.length} approved</div>
        </div>
      </section>

      <section className="bg-neutral-100 text-neutral-900 rounded-xl border border-neutral-200 p-6">
        <div className="flex items-center justify-between"><h3 className="text-xl font-semibold">Guest reviews</h3></div>
        <div className="grid md:grid-cols-2 gap-4 mt-5">
          {rows.map(r => (
            <div key={r.review_id} className="bg-white rounded-xl border border-neutral-200 p-4">
              <div className="flex items-center justify-between mb-2 text-sm text-neutral-500">
                <div>{r.author_name || 'Guest'} • {r.submitted_at.slice(0,10)}</div>
                {r.rating_overall != null && (<div className="px-2 py-0.5 rounded-full border border-neutral-300 text-neutral-800 font-semibold">{r.rating_overall.toFixed(1)}</div>)}
              </div>
              <div className="text-neutral-900 leading-7">{r.text_public}</div>
            </div>
          ))}
          {!rows.length && (
            <div className="text-neutral-400">No approved reviews yet.</div>
          )}
        </div>
      </section>
    </main>
  )
}



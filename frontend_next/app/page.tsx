export default function HomePage() {
  return (
    <main className="container-narrow py-8">
      <h1 className="text-3xl font-bold">Flex Living Reviews</h1>
      <p className="text-neutral-300 mt-2">Choose a page:</p>
      <div className="grid md:grid-cols-2 gap-4 mt-6">
        <a href="/dashboard" className="card p-6 hover:border-brand-accent">
          <h2 className="text-xl font-semibold">Manager Dashboard →</h2>
          <p className="text-neutral-300 mt-2">Filter, inspect, and approve reviews.</p>
        </a>
        <a href="/property" className="card p-6 hover:border-brand-accent">
          <h2 className="text-xl font-semibold">Property Reviews →</h2>
          <p className="text-neutral-300 mt-2">Public-style section with approved reviews.</p>
        </a>
      </div>
    </main>
  )
}



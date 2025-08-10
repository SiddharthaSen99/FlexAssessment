import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Flex Reviews',
  description: 'Flex Living Reviews Dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-neutral-800/80">
          <div className="container-narrow py-4 flex items-center justify-between">
            <Link href="/" className="text-lg font-semibold hover:text-brand-accent">Flex Reviews</Link>
            <nav className="flex items-center gap-2">
              <Link href="/dashboard" className="card px-3 py-2 hover:border-brand-accent">Manager Dashboard</Link>
              <Link href="/property" className="card px-3 py-2 hover:border-brand-accent">Property Reviews</Link>
              <Link href="/google" className="card px-3 py-2 hover:border-brand-accent">Google Reviews</Link>
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  )
}



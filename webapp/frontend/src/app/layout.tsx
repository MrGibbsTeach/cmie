import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CMIE Studio',
  description: 'AI-powered curriculum generation',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950">
        <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold text-sm">
                C
              </div>
              <span className="font-semibold text-white text-sm tracking-tight">CMIE Studio</span>
            </a>
            <a
              href="/builder"
              className="px-4 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-sm font-medium transition-colors"
            >
              + New Generation
            </a>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-10">{children}</main>
      </body>
    </html>
  )
}

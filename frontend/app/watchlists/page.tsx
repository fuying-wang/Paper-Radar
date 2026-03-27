import Link from "next/link";

import { fetchLinkedInWatchlist } from "@/lib/api";

export default async function WatchlistsPage() {
  const watchlistItems = await fetchLinkedInWatchlist();

  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto w-full max-w-6xl">
        <header className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-semibold text-slate-900">Watchlists</h1>
          <p className="mt-2 text-sm text-slate-600">LinkedIn Watchlist (Phase 2) manual configuration overview.</p>
        </header>

        <section className="mt-6 space-y-3">
          {watchlistItems.length === 0 ? (
            <article className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600 shadow-sm">
              No LinkedIn watchlist items configured.
            </article>
          ) : null}
          {watchlistItems.map((item) => (
            <article key={item.id} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-sm font-semibold text-slate-900">{item.name}</p>
              <p className="mt-1 text-xs text-slate-600">{item.entity_type}</p>
              {item.notes ? <p className="mt-2 text-sm text-slate-700">{item.notes}</p> : null}
              <div className="mt-3">
                <Link href={item.linkedin_url} target="_blank" className="text-sm font-medium text-slate-700 underline">
                  Open LinkedIn
                </Link>
              </div>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}

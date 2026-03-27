"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { MOCK_PAPERS, type PaperRecord } from "@/lib/mock-papers";

type SortTab = "latest" | "hot" | "influential";
type SortMode = "score" | "citations" | "year";

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get("query")?.trim() || "machine learning";

  const [activeTab, setActiveTab] = useState<SortTab>("latest");
  const [yearFilter, setYearFilter] = useState<string>("all");
  const [venueFilter, setVenueFilter] = useState<string>("all");
  const [sortMode, setSortMode] = useState<SortMode>("score");
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});

  const yearOptions = useMemo(
    () => [...new Set(MOCK_PAPERS.map((paper) => paper.year))].sort((a, b) => b - a),
    [],
  );

  const venueOptions = useMemo(
    () => [...new Set(MOCK_PAPERS.map((paper) => paper.venue))].sort(),
    [],
  );

  const displayedPapers = useMemo(() => {
    const scoreField: Record<SortTab, keyof PaperRecord> = {
      latest: "latest_score",
      hot: "hot_score",
      influential: "influential_score",
    };

    const filtered = MOCK_PAPERS.filter((paper) => {
      const yearMatched = yearFilter === "all" || String(paper.year) === yearFilter;
      const venueMatched = venueFilter === "all" || paper.venue === venueFilter;
      return yearMatched && venueMatched;
    });

    const sorted = [...filtered].sort((a, b) => {
      if (sortMode === "citations") {
        return b.cited_by_count - a.cited_by_count;
      }
      if (sortMode === "year") {
        return b.year - a.year;
      }
      const key = scoreField[activeTab];
      return Number(b[key]) - Number(a[key]);
    });

    return sorted;
  }, [activeTab, sortMode, venueFilter, yearFilter]);

  const toggleFavorite = (paperId: string) => {
    setFavorites((previous) => ({
      ...previous,
      [paperId]: !previous[paperId],
    }));
  };

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <section className="mx-auto w-full max-w-5xl">
        <header className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Query</p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">{query}</h1>
          <p className="mt-2 text-sm text-slate-600">
            Explore ranked research papers and switch views by recency, momentum, or impact.
          </p>
        </header>

        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-center gap-2">
            {(["latest", "hot", "influential"] as SortTab[]).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  activeTab === tab
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {tab === "latest" ? "Latest" : tab === "hot" ? "Hot" : "Influential"}
              </button>
            ))}
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <select
              value={yearFilter}
              onChange={(event) => setYearFilter(event.target.value)}
              className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700"
            >
              <option value="all">All Years</option>
              {yearOptions.map((year) => (
                <option key={year} value={String(year)}>
                  {year}
                </option>
              ))}
            </select>

            <select
              value={venueFilter}
              onChange={(event) => setVenueFilter(event.target.value)}
              className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700"
            >
              <option value="all">All Venues</option>
              {venueOptions.map((venue) => (
                <option key={venue} value={venue}>
                  {venue}
                </option>
              ))}
            </select>

            <select
              value={sortMode}
              onChange={(event) => setSortMode(event.target.value as SortMode)}
              className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700"
            >
              <option value="score">Sort by Tab Score</option>
              <option value="citations">Sort by Citations</option>
              <option value="year">Sort by Year</option>
            </select>
          </div>
        </section>

        <section className="mt-6 space-y-4">
          {displayedPapers.map((paper) => (
            <article
              key={paper.id}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow"
            >
              <h2 className="text-lg font-semibold text-slate-900">
                <Link
                  href={`/papers/${encodeURIComponent(paper.id)}`}
                  className="hover:text-slate-700 hover:underline"
                >
                  {paper.title}
                </Link>
              </h2>
              <p className="mt-2 text-sm text-slate-600">{paper.authors.join(", ")}</p>
              <p className="mt-1 text-sm text-slate-600">
                {paper.venue} · {paper.year}
              </p>
              <p className="mt-1 text-sm font-medium text-slate-700">
                Citations: {paper.cited_by_count}
              </p>
              <p className="mt-4 text-sm leading-6 text-slate-700">{paper.abstract}</p>

              <div className="mt-5 flex flex-wrap gap-3">
                <Link
                  href={paper.url}
                  target="_blank"
                  className="inline-flex items-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
                >
                  Open Link
                </Link>
                <button
                  type="button"
                  onClick={() => toggleFavorite(paper.id)}
                  className="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                >
                  {favorites[paper.id] ? "Saved" : "Favorite"}
                </button>
                <Link
                  href={`/papers/${encodeURIComponent(paper.id)}`}
                  className="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                >
                  Details
                </Link>
              </div>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}

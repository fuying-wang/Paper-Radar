"use client";

import Link from "next/link";
import { type FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

type SortTab = "latest" | "hot" | "influential" | "social_buzz";
type SortMode = "score" | "citations" | "year";
type ResultPaper = {
  id: string;
  title: string;
  authors: string[];
  venue: string;
  year: number;
  abstract: string;
  cited_by_count: number;
  url: string;
  latest_score: number;
  hot_score: number;
  influential_score: number;
  final_score: number;
  source_name?: string;
  primary_topic?: string;
  topic_tags?: string[];
};

type SocialPost = {
  id: string;
  text: string;
  author: string;
  created_at: string;
  post_url: string;
  public_metrics: {
    like_count: number;
    retweet_count: number;
    reply_count: number;
    quote_count: number;
    bookmark_count: number;
    impression_count: number;
  };
  primary_topic: string;
  topic_tags: string[];
};

type ResultsClientProps = {
  query: string;
  source: string;
  initialSortTab: "latest" | "hot" | "influential" | "social_buzz";
  papers: ResultPaper[];
  socialPosts: SocialPost[];
  linkedInWatchlistItems: Array<{
    id: number;
    entity_type: "institution" | "lab" | "author" | "company_page";
    name: string;
    linkedin_url: string;
    notes: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }>;
};

export default function ResultsClient({
  query,
  source,
  initialSortTab,
  papers,
  socialPosts,
  linkedInWatchlistItems,
}: ResultsClientProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<SortTab>(initialSortTab);
  const [yearFilter, setYearFilter] = useState<string>("all");
  const [venueFilter, setVenueFilter] = useState<string>("all");
  const [sortMode, setSortMode] = useState<SortMode>("score");
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});
  const [watchlistItems, setWatchlistItems] = useState(linkedInWatchlistItems);
  const [entityType, setEntityType] = useState<"institution" | "lab" | "author" | "company_page">("institution");
  const [entityName, setEntityName] = useState("");
  const [entityUrl, setEntityUrl] = useState("");
  const [entityNotes, setEntityNotes] = useState("");

  const yearOptions = useMemo(
    () => [...new Set(papers.map((paper) => paper.year))].sort((a, b) => b - a),
    [papers],
  );

  const venueOptions = useMemo(
    () => [...new Set(papers.map((paper) => paper.venue))].sort(),
    [papers],
  );

  const displayedPapers = useMemo(() => {
    const scoreField: Record<SortTab, keyof ResultPaper> = {
      latest: "latest_score",
      hot: "hot_score",
      influential: "influential_score",
      social_buzz: "hot_score",
    };

    const filtered = papers.filter((paper) => {
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
  }, [activeTab, papers, sortMode, venueFilter, yearFilter]);

  const toggleFavorite = (paperId: string) => {
    setFavorites((previous) => ({
      ...previous,
      [paperId]: !previous[paperId],
    }));
  };

  const handleSourceChange = (nextSource: string) => {
    const params = new URLSearchParams();
    params.set("query", query);
    params.set("source", nextSource);
    params.set("sort_by", activeTab);
    router.push(`/results?${params.toString()}`);
  };

  const handleSortTabChange = (nextTab: SortTab) => {
    setActiveTab(nextTab);
    const params = new URLSearchParams();
    params.set("query", query);
    params.set("source", source);
    params.set("sort_by", nextTab);
    router.push(`/results?${params.toString()}`);
  };

  const handleAddWatchlistItem = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    if (!apiBaseUrl || !entityName.trim() || !entityUrl.trim()) {
      return;
    }
    const response = await fetch(`${apiBaseUrl}/watchlists/linkedin`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        entity_type: entityType,
        name: entityName.trim(),
        linkedin_url: entityUrl.trim(),
        notes: entityNotes.trim(),
        is_active: true,
      }),
    });
    if (!response.ok) {
      return;
    }
    const createdItem = (await response.json()) as ResultsClientProps["linkedInWatchlistItems"][number];
    setWatchlistItems((previous) => [createdItem, ...previous]);
    setEntityName("");
    setEntityUrl("");
    setEntityNotes("");
  };

  const handleDeleteWatchlistItem = async (id: number) => {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    if (!apiBaseUrl) {
      return;
    }
    const response = await fetch(`${apiBaseUrl}/watchlists/linkedin/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      return;
    }
    setWatchlistItems((previous) => previous.filter((item) => item.id !== id));
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
            {(["latest", "hot", "influential", "social_buzz"] as SortTab[]).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => handleSortTabChange(tab)}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  activeTab === tab
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {tab === "latest"
                  ? "Latest"
                  : tab === "hot"
                    ? "Hot"
                    : tab === "influential"
                      ? "Influential"
                      : "Social Buzz"}
              </button>
            ))}
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-4">
            <select
              value={source}
              onChange={(event) => handleSourceChange(event.target.value)}
              className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700"
            >
              <option value="all">All Sources</option>
              <option value="openalex">OpenAlex</option>
              <option value="semantic_scholar">Semantic Scholar</option>
              <option value="arxiv">arXiv</option>
              <option value="journal">Journals</option>
            </select>

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
          {displayedPapers.length === 0 ? (
            <article className="rounded-2xl border border-slate-200 bg-white p-8 text-sm text-slate-600 shadow-sm">
              No papers found for this query. Try another keyword.
            </article>
          ) : null}
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
              <div className="mt-2 flex flex-wrap gap-2">
                <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                  Source: {paper.source_name || "unknown"}
                </span>
                {paper.source_name === "journal" ? (
                  <span className="rounded-full bg-indigo-100 px-2 py-1 text-xs font-medium text-indigo-700">
                    Journal: {paper.venue}
                  </span>
                ) : null}
                {paper.primary_topic ? (
                  <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-700">
                    Topic: {paper.primary_topic}
                  </span>
                ) : null}
                {(paper.topic_tags ?? []).slice(0, 3).map((tag) => (
                  <span key={`${paper.id}-${tag}`} className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
                    {tag}
                  </span>
                ))}
              </div>
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

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Social Buzz</h2>
          <p className="mt-1 text-sm text-slate-600">Latest X posts related to your query</p>
          <div className="mt-4 space-y-3">
            {socialPosts.length === 0 ? (
              <article className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                No social posts available for this query.
              </article>
            ) : null}
            {socialPosts.map((post) => (
              <article key={post.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-800">{post.text}</p>
                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-600">
                  <span className="rounded-full bg-white px-2 py-1">Author: @{post.author}</span>
                  <span className="rounded-full bg-white px-2 py-1">Topic: {post.primary_topic}</span>
                  <span className="rounded-full bg-white px-2 py-1">Likes: {post.public_metrics.like_count}</span>
                  <span className="rounded-full bg-white px-2 py-1">Retweets: {post.public_metrics.retweet_count}</span>
                  <span className="rounded-full bg-white px-2 py-1">Replies: {post.public_metrics.reply_count}</span>
                </div>
                <div className="mt-3">
                  <Link href={post.post_url} target="_blank" className="text-sm font-medium text-slate-700 underline">
                    Open on X
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">LinkedIn Watchlist (Phase 2)</h2>
          <p className="mt-1 text-sm text-slate-600">
            Manual watchlist for institutions, labs, authors, and company pages. Auto-fetch connector is reserved.
          </p>

          <form onSubmit={handleAddWatchlistItem} className="mt-4 grid gap-3 sm:grid-cols-4">
            <select
              value={entityType}
              onChange={(event) =>
                setEntityType(event.target.value as "institution" | "lab" | "author" | "company_page")
              }
              className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700"
            >
              <option value="institution">Institution</option>
              <option value="lab">Lab</option>
              <option value="author">Author</option>
              <option value="company_page">Company Page</option>
            </select>
            <input
              type="text"
              value={entityName}
              onChange={(event) => setEntityName(event.target.value)}
              placeholder="Name"
              className="h-10 rounded-lg border border-slate-300 px-3 text-sm text-slate-700"
            />
            <input
              type="url"
              value={entityUrl}
              onChange={(event) => setEntityUrl(event.target.value)}
              placeholder="LinkedIn URL"
              className="h-10 rounded-lg border border-slate-300 px-3 text-sm text-slate-700"
            />
            <button
              type="submit"
              className="h-10 rounded-lg bg-slate-900 px-4 text-sm font-medium text-white transition hover:bg-slate-800"
            >
              Add Watch Item
            </button>
            <input
              type="text"
              value={entityNotes}
              onChange={(event) => setEntityNotes(event.target.value)}
              placeholder="Notes (optional)"
              className="sm:col-span-4 h-10 rounded-lg border border-slate-300 px-3 text-sm text-slate-700"
            />
          </form>

          <div className="mt-4 space-y-3">
            {watchlistItems.length === 0 ? (
              <article className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                No LinkedIn watchlist items yet.
              </article>
            ) : null}
            {watchlistItems.map((item) => (
              <article key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium text-slate-900">{item.name}</p>
                    <p className="text-xs text-slate-600">{item.entity_type}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDeleteWatchlistItem(item.id)}
                    className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
                  >
                    Remove
                  </button>
                </div>
                <div className="mt-2">
                  <Link href={item.linkedin_url} target="_blank" className="text-sm text-slate-700 underline">
                    Open LinkedIn
                  </Link>
                </div>
                {item.notes ? <p className="mt-2 text-xs text-slate-600">{item.notes}</p> : null}
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

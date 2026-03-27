import Link from "next/link";

import { fetchPapers, fetchSocialBuzz } from "@/lib/api";

type DashboardBlockProps = {
  title: string;
  href: string;
  items: Array<{ id: string; title: string; topic?: string }>;
};

function DashboardBlock({ title, href, items }: DashboardBlockProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
        <Link href={href} className="text-sm font-medium text-slate-700 underline">
          View
        </Link>
      </div>
      <div className="mt-4 space-y-3">
        {items.length === 0 ? <p className="text-sm text-slate-600">No data yet.</p> : null}
        {items.map((item) => (
          <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <p className="text-sm font-medium text-slate-900">{item.title}</p>
            {item.topic ? <p className="mt-1 text-xs text-emerald-700">{item.topic}</p> : null}
          </div>
        ))}
      </div>
    </article>
  );
}

export default async function HomePage() {
  const [mustRead, explodingTopics, healthcare, general, crossovers, conference, social] = await Promise.all([
    fetchPapers({ query: "healthcare ai llm", sortBy: "influential", limit: 5 }),
    fetchPapers({ query: "agent reasoning mllm", sortBy: "hot", limit: 5 }),
    fetchPapers({ query: "healthcare ai medical reasoning", sortBy: "latest", limit: 5 }),
    fetchPapers({ query: "general ai frontier llm", sortBy: "latest", limit: 5 }),
    fetchPapers({ query: "medical mllm healthcare agent", sortBy: "latest", limit: 5 }),
    fetchPapers({ query: "iclr conference openreview", sortBy: "latest", limit: 5 }),
    fetchSocialBuzz("healthcare ai llm", 5),
  ]);

  const socialItems = social.map((item) => ({
    id: item.id,
    title: item.text,
    topic: item.primary_topic,
  }));

  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto w-full max-w-6xl">
        <header className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <h1 className="text-4xl font-semibold tracking-tight text-slate-900">Research Radar Dashboard</h1>
          <p className="mt-3 text-base text-slate-600">
            Unified intelligence panel across papers, journals, conferences, social buzz, and watchlists.
          </p>

          <form action="/results" method="get" className="mt-8 flex flex-col gap-3 sm:flex-row">
            <input
              name="query"
              type="text"
              placeholder="Enter research field or keywords"
              defaultValue="healthcare ai"
              className="h-12 flex-1 rounded-lg border border-slate-300 px-4 text-base text-slate-900 outline-none transition focus:border-slate-500"
            />
            <button
              type="submit"
              className="h-12 rounded-lg bg-slate-900 px-6 text-base font-medium text-white transition hover:bg-slate-800"
            >
              Search
            </button>
          </form>
        </header>

        <section className="mt-6 grid gap-4 lg:grid-cols-2">
          <DashboardBlock
            title="Must Read Today"
            href="/results?query=healthcare%20ai&sort_by=influential"
            items={mustRead.map((item) => ({ id: item.id, title: item.title, topic: item.primary_topic }))}
          />
          <DashboardBlock
            title="Exploding Topics"
            href="/results?query=agent%20reasoning&sort_by=hot"
            items={explodingTopics.map((item) => ({ id: item.id, title: item.title, topic: item.primary_topic }))}
          />
          <DashboardBlock
            title="Healthcare AI updates"
            href="/healthcare-ai"
            items={healthcare.map((item) => ({ id: item.id, title: item.title, topic: item.primary_topic }))}
          />
          <DashboardBlock
            title="General AI Frontier updates"
            href="/general-ai-frontier"
            items={general.map((item) => ({ id: item.id, title: item.title, topic: item.primary_topic }))}
          />
          <DashboardBlock
            title="Crossovers"
            href="/crossovers"
            items={crossovers.map((item) => ({ id: item.id, title: item.title, topic: item.primary_topic }))}
          />
          <DashboardBlock
            title="Conference Radar"
            href="/conferences"
            items={conference.map((item) => ({ id: item.id, title: item.title, topic: item.primary_topic }))}
          />
          <DashboardBlock title="Social Buzz" href="/social-buzz" items={socialItems} />
        </section>
      </section>
    </main>
  );
}

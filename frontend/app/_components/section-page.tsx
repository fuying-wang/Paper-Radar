import Link from "next/link";

import { type PaperItem, fetchPapers } from "@/lib/api";

type SectionPageProps = {
  title: string;
  description: string;
  query: string;
  source?: "all" | "openalex" | "semantic_scholar" | "arxiv" | "journal";
};

function TopicTags({ paper }: { paper: PaperItem }) {
  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {paper.primary_topic ? (
        <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-700">
          {paper.primary_topic}
        </span>
      ) : null}
      {(paper.topic_tags ?? []).slice(0, 4).map((tag) => (
        <span key={`${paper.id}-${tag}`} className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
          {tag}
        </span>
      ))}
    </div>
  );
}

export default async function SectionPage({ title, description, query, source = "all" }: SectionPageProps) {
  const [latest, hot, influential, socialBuzz] = await Promise.all([
    fetchPapers({ query, source, sortBy: "latest", limit: 8 }),
    fetchPapers({ query, source, sortBy: "hot", limit: 8 }),
    fetchPapers({ query, source, sortBy: "influential", limit: 8 }),
    fetchPapers({ query, source, sortBy: "social_buzz", limit: 8 }),
  ]);

  const groups = [
    { name: "Latest", papers: latest },
    { name: "Hot", papers: hot },
    { name: "Influential", papers: influential },
    { name: "Social Buzz", papers: socialBuzz },
  ];

  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto w-full max-w-6xl">
        <header className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-semibold text-slate-900">{title}</h1>
          <p className="mt-2 text-sm text-slate-600">{description}</p>
        </header>

        <section className="mt-6 grid gap-4 lg:grid-cols-2">
          {groups.map((group) => (
            <article key={group.name} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900">{group.name}</h2>
              <div className="mt-4 space-y-3">
                {group.papers.length === 0 ? (
                  <p className="text-sm text-slate-600">No data available.</p>
                ) : null}
                {group.papers.map((paper) => (
                  <div key={`${group.name}-${paper.id}`} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <Link href={`/papers/${encodeURIComponent(paper.id)}`} className="text-sm font-semibold text-slate-900 hover:underline">
                      {paper.title}
                    </Link>
                    <p className="mt-1 text-xs text-slate-600">
                      {paper.venue} · {paper.year} · {paper.source_name ?? "unknown"}
                    </p>
                    <TopicTags paper={paper} />
                  </div>
                ))}
              </div>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}

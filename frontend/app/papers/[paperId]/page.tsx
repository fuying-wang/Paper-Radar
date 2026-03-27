import Link from "next/link";
import { notFound } from "next/navigation";

import { MOCK_PAPERS } from "@/lib/mock-papers";

type PaperDetailPageProps = {
  params: {
    paperId: string;
  };
};

export default function PaperDetailPage({ params }: PaperDetailPageProps) {
  const decodedId = decodeURIComponent(params.paperId);
  const paper = MOCK_PAPERS.find((item) => item.id === decodedId);

  if (!paper) {
    notFound();
  }

  const sourceLabel = paper.source_name === "openalex" ? "OpenAlex" : "Semantic Scholar";
  const relatedPapers = paper.related_ids
    .map((relatedId) => MOCK_PAPERS.find((item) => item.id === relatedId))
    .filter((item) => item !== undefined);

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <section className="mx-auto w-full max-w-4xl">
        <div className="mb-4">
          <Link href="/results" className="text-sm font-medium text-slate-600 hover:text-slate-900">
            ← Back to Results
          </Link>
        </div>

        <article className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Paper Detail</p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">{paper.title}</h1>
          <p className="mt-3 text-sm text-slate-600">{paper.authors.join(", ")}</p>
          <p className="mt-1 text-sm text-slate-600">
            {paper.venue} · {paper.year}
          </p>
          <p className="mt-1 text-sm font-medium text-slate-700">Citations: {paper.cited_by_count}</p>

          <section className="mt-7">
            <h2 className="text-base font-semibold text-slate-900">Abstract</h2>
            <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-700">{paper.abstract}</p>
          </section>

          <section className="mt-7">
            <h2 className="text-base font-semibold text-slate-900">Score Breakdown</h2>
            <div className="mt-3 grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs text-slate-500">latest_score</p>
                <p className="mt-1 text-lg font-semibold text-slate-900">{paper.latest_score.toFixed(2)}</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs text-slate-500">hot_score</p>
                <p className="mt-1 text-lg font-semibold text-slate-900">{paper.hot_score.toFixed(2)}</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs text-slate-500">influential_score</p>
                <p className="mt-1 text-lg font-semibold text-slate-900">{paper.influential_score.toFixed(2)}</p>
              </div>
            </div>
          </section>

          <section className="mt-7 grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs text-slate-500">Source</p>
              <p className="mt-1 text-sm font-medium text-slate-900">{sourceLabel}</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs text-slate-500">DOI</p>
              <p className="mt-1 break-all text-sm font-medium text-slate-900">{paper.doi || "N/A"}</p>
            </div>
          </section>

          <section className="mt-5 flex flex-wrap gap-3">
            {paper.doi ? (
              <Link
                href={`https://doi.org/${paper.doi}`}
                target="_blank"
                className="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
              >
                Open DOI
              </Link>
            ) : null}
            <Link
              href={paper.url}
              target="_blank"
              className="inline-flex items-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
            >
              Open Original Link
            </Link>
          </section>
        </article>

        {relatedPapers.length > 0 ? (
          <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Related Papers</h2>
            <div className="mt-4 space-y-3">
              {relatedPapers.map((relatedPaper) => (
                <Link
                  key={relatedPaper.id}
                  href={`/papers/${encodeURIComponent(relatedPaper.id)}`}
                  className="block rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 transition hover:border-slate-300 hover:bg-slate-100"
                >
                  <p className="text-sm font-medium text-slate-900">{relatedPaper.title}</p>
                  <p className="mt-1 text-xs text-slate-600">
                    {relatedPaper.venue} · {relatedPaper.year}
                  </p>
                </Link>
              ))}
            </div>
          </section>
        ) : null}
      </section>
    </main>
  );
}

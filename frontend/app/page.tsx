import Link from "next/link";

const recentSearches = [
  "llm for biology",
  "graph neural networks",
  "multimodal retrieval",
  "robotics manipulation",
];

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-12">
      <section className="mx-auto w-full max-w-4xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-4xl font-semibold tracking-tight text-slate-900">Research Radar</h1>
        <p className="mt-3 text-base text-slate-600">
          Discover latest, hot, and influential papers across research domains.
        </p>

        <form action="/results" method="get" className="mt-8 flex flex-col gap-3 sm:flex-row">
          <input
            name="query"
            type="text"
            placeholder="Enter research field or keywords"
            defaultValue="machine learning"
            className="h-12 flex-1 rounded-lg border border-slate-300 px-4 text-base text-slate-900 outline-none transition focus:border-slate-500"
          />
          <button
            type="submit"
            className="h-12 rounded-lg bg-slate-900 px-6 text-base font-medium text-white transition hover:bg-slate-800"
          >
            Search
          </button>
        </form>

        <section className="mt-10">
          <h2 className="text-lg font-medium text-slate-900">Recent Searches</h2>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {recentSearches.map((item) => (
              <li key={item}>
                <Link
                  href={`/results?query=${encodeURIComponent(item)}`}
                  className="block rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 transition hover:border-slate-300 hover:bg-slate-100"
                >
                  {item}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </section>
    </main>
  );
}

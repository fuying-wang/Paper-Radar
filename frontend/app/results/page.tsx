import ResultsClient from "./results-client";
import { MOCK_PAPERS } from "@/lib/mock-papers";

type ResultsPageProps = {
  searchParams: Promise<{
    query?: string;
  }>;
};

type SearchResponse = {
  keyword: string;
  papers: Array<{
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
  }>;
};

async function fetchPapers(query: string): Promise<SearchResponse["papers"]> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!apiBaseUrl) {
    return MOCK_PAPERS.map((paper) => ({
      id: paper.id,
      title: paper.title,
      authors: paper.authors,
      venue: paper.venue,
      year: paper.year,
      abstract: paper.abstract,
      cited_by_count: paper.cited_by_count,
      url: paper.url,
      latest_score: paper.latest_score,
      hot_score: paper.hot_score,
      influential_score: paper.influential_score,
      final_score: paper.final_score,
    }));
  }

  const requestUrl = `${apiBaseUrl}/papers/search?keyword=${encodeURIComponent(query)}&sort_by=latest&limit=50`;
  try {
    const response = await fetch(requestUrl, { cache: "no-store" });
    if (!response.ok) {
      return [];
    }
    const payload = (await response.json()) as SearchResponse;
    return payload.papers ?? [];
  } catch {
    return [];
  }
}

export default async function ResultsPage({ searchParams }: ResultsPageProps) {
  const resolvedSearchParams = await searchParams;
  const query = resolvedSearchParams.query?.trim() || "machine learning";
  const papers = await fetchPapers(query);
  return <ResultsClient query={query} papers={papers} />;
}

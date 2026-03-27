import ResultsClient from "./results-client";
import { fetchLinkedInWatchlist, fetchPapers, fetchSocialBuzz } from "@/lib/api";
import { MOCK_PAPERS } from "@/lib/mock-papers";

type ResultsPageProps = {
  searchParams: Promise<{
    query?: string;
    source?: string;
    sort_by?: string;
  }>;
};

function buildMockPapers(query: string) {
  const normalizedQuery = query.trim().toLowerCase();
  const mapped = MOCK_PAPERS.map((paper) => ({
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
    source_name: paper.source_name,
  }));
  if (!normalizedQuery) {
    return mapped;
  }
  const filtered = mapped.filter((paper) => {
    const text = `${paper.title} ${paper.abstract} ${paper.venue}`.toLowerCase();
    return text.includes(normalizedQuery);
  });
  return filtered.length > 0 ? filtered : mapped;
}

export default async function ResultsPage({ searchParams }: ResultsPageProps) {
  const resolvedSearchParams = await searchParams;
  const query = resolvedSearchParams.query?.trim() || "machine learning";
  const source = (resolvedSearchParams.source?.trim() || "all") as
    | "all"
    | "openalex"
    | "semantic_scholar"
    | "arxiv"
    | "journal";
  const sortBy = (resolvedSearchParams.sort_by?.trim() || "latest") as
    | "latest"
    | "hot"
    | "influential"
    | "social_buzz";
  const apiPapers = await fetchPapers({ query, source, sortBy, limit: 50 });
  const papers = apiPapers.length > 0 ? apiPapers : buildMockPapers(query);
  const socialPosts = await fetchSocialBuzz(query);
  const linkedInWatchlistItems = await fetchLinkedInWatchlist();
  return (
    <ResultsClient
      query={query}
      source={source}
      initialSortTab={sortBy}
      papers={papers}
      socialPosts={socialPosts}
      linkedInWatchlistItems={linkedInWatchlistItems}
    />
  );
}

import ResultsClient from "./results-client";

type ResultsPageProps = {
  searchParams: Promise<{
    query?: string;
  }>;
};

export default async function ResultsPage({ searchParams }: ResultsPageProps) {
  const resolvedSearchParams = await searchParams;
  const query = resolvedSearchParams.query?.trim() || "machine learning";
  return <ResultsClient query={query} />;
}

import { MOCK_PAPERS } from "./mock-papers";

export type PaperItem = {
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

export type SocialItem = {
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

export type LinkedInWatchlistItem = {
  id: number;
  entity_type: "institution" | "lab" | "author" | "company_page";
  name: string;
  linkedin_url: string;
  notes: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

const MOCK_WATCHLIST_ITEMS: LinkedInWatchlistItem[] = [
  {
    id: 1,
    entity_type: "institution",
    name: "Stanford HAI",
    linkedin_url: "https://www.linkedin.com/company/stanford-hai/",
    notes: "Healthcare agent updates",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    entity_type: "company_page",
    name: "Google DeepMind",
    linkedin_url: "https://www.linkedin.com/company/google-deepmind/",
    notes: "General AI frontier releases",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function classifyMockTopic(text: string): { primary_topic: string; topic_tags: string[] } {
  const normalized = text.toLowerCase();
  const healthcareHits = ["medical", "clinical", "healthcare", "biomedical"].filter((k) => normalized.includes(k));
  const generalHits = ["llm", "mllm", "agent", "reasoning", "rag"].filter((k) => normalized.includes(k));
  if (healthcareHits.length > 0 && generalHits.length > 0) {
    return { primary_topic: "Crossovers", topic_tags: [...healthcareHits, ...generalHits].slice(0, 4) };
  }
  if (healthcareHits.length > 0) {
    return { primary_topic: "Healthcare AI", topic_tags: healthcareHits.slice(0, 4) };
  }
  return { primary_topic: "General AI", topic_tags: generalHits.slice(0, 4) };
}

function buildMockPaperFallback(params: {
  query: string;
  source?: "all" | "openalex" | "semantic_scholar" | "arxiv" | "journal";
  sortBy?: "latest" | "hot" | "influential" | "social_buzz";
  limit?: number;
}): PaperItem[] {
  const source = params.source ?? "all";
  const sortBy = params.sortBy ?? "latest";
  const limit = params.limit ?? 20;
  const normalizedQuery = params.query.trim().toLowerCase();
  const mapped: PaperItem[] = MOCK_PAPERS.map((paper) => {
    const topic = classifyMockTopic(`${paper.title} ${paper.abstract} ${paper.venue}`);
    return {
      id: paper.id,
      title: paper.title,
      authors: paper.authors,
      venue: source === "journal" ? "Nature Machine Intelligence" : paper.venue,
      year: paper.year,
      abstract: paper.abstract,
      cited_by_count: paper.cited_by_count,
      url: paper.url,
      latest_score: paper.latest_score,
      hot_score: paper.hot_score,
      influential_score: paper.influential_score,
      final_score: paper.final_score,
      source_name: source === "journal" ? "journal" : source === "arxiv" ? "arxiv" : source === "semantic_scholar" ? "semantic_scholar" : paper.source_name,
      primary_topic: topic.primary_topic,
      topic_tags: topic.topic_tags,
    };
  });
  const sourceFiltered = source === "all" ? mapped : mapped.filter((paper) => (paper.source_name ?? "") === source);
  const queryFiltered = normalizedQuery
    ? sourceFiltered.filter((paper) => `${paper.title} ${paper.abstract} ${paper.venue}`.toLowerCase().includes(normalizedQuery))
    : sourceFiltered;
  const safeItems = queryFiltered.length > 0 ? queryFiltered : sourceFiltered.length > 0 ? sourceFiltered : mapped;
  const sorted = [...safeItems].sort((a, b) => {
    if (sortBy === "hot" || sortBy === "social_buzz") return b.hot_score - a.hot_score;
    if (sortBy === "influential") return b.influential_score - a.influential_score;
    return b.latest_score - a.latest_score;
  });
  return sorted.slice(0, limit);
}

function buildMockSocialFallback(query: string, limit: number): SocialItem[] {
  const base = buildMockPaperFallback({ query, sortBy: "hot", limit });
  const now = new Date().toISOString();
  return base.slice(0, limit).map((paper, index) => ({
    id: `mock-social-${paper.id}-${index}`,
    text: `${paper.title} — ${paper.abstract.slice(0, 120)}...`,
    author: "research-radar",
    created_at: now,
    post_url: paper.url,
    public_metrics: {
      like_count: 20 + index * 7,
      retweet_count: 5 + index * 3,
      reply_count: 2 + index,
      quote_count: 1,
      bookmark_count: 3,
      impression_count: 500 + index * 120,
    },
    primary_topic: paper.primary_topic ?? "General AI",
    topic_tags: paper.topic_tags ?? [],
  }));
}

export async function fetchPapers(params: {
  query: string;
  source?: "all" | "openalex" | "semantic_scholar" | "arxiv" | "journal";
  sortBy?: "latest" | "hot" | "influential" | "social_buzz";
  limit?: number;
}): Promise<PaperItem[]> {
  if (!apiBaseUrl) {
    return buildMockPaperFallback(params);
  }
  const source = params.source ?? "all";
  const sortBy = params.sortBy ?? "latest";
  const limit = params.limit ?? 20;
  const url = `${apiBaseUrl}/papers/search?keyword=${encodeURIComponent(params.query)}&source=${encodeURIComponent(source)}&sort_by=${encodeURIComponent(sortBy)}&limit=${limit}`;
  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      return buildMockPaperFallback(params);
    }
    const payload = (await response.json()) as { papers?: PaperItem[] };
    if (!payload.papers || payload.papers.length === 0) {
      return buildMockPaperFallback(params);
    }
    return payload.papers;
  } catch {
    return buildMockPaperFallback(params);
  }
}

export async function fetchSocialBuzz(query: string, limit: number = 10): Promise<SocialItem[]> {
  if (!apiBaseUrl) {
    return buildMockSocialFallback(query, limit);
  }
  const url = `${apiBaseUrl}/social/search?keyword=${encodeURIComponent(query)}&limit=${limit}`;
  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      return buildMockSocialFallback(query, limit);
    }
    const payload = (await response.json()) as { posts?: SocialItem[] };
    if (!payload.posts || payload.posts.length === 0) {
      return buildMockSocialFallback(query, limit);
    }
    return payload.posts;
  } catch {
    return buildMockSocialFallback(query, limit);
  }
}

export async function fetchLinkedInWatchlist(): Promise<LinkedInWatchlistItem[]> {
  if (!apiBaseUrl) {
    return MOCK_WATCHLIST_ITEMS;
  }
  try {
    const response = await fetch(`${apiBaseUrl}/watchlists/linkedin`, { cache: "no-store" });
    if (!response.ok) {
      return MOCK_WATCHLIST_ITEMS;
    }
    const payload = (await response.json()) as { items?: LinkedInWatchlistItem[] };
    if (!payload.items || payload.items.length === 0) {
      return MOCK_WATCHLIST_ITEMS;
    }
    return payload.items;
  } catch {
    return MOCK_WATCHLIST_ITEMS;
  }
}

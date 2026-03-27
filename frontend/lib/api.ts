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

export async function fetchPapers(params: {
  query: string;
  source?: "all" | "openalex" | "semantic_scholar" | "arxiv" | "journal";
  sortBy?: "latest" | "hot" | "influential" | "social_buzz";
  limit?: number;
}): Promise<PaperItem[]> {
  if (!apiBaseUrl) {
    return [];
  }
  const source = params.source ?? "all";
  const sortBy = params.sortBy ?? "latest";
  const limit = params.limit ?? 20;
  const url = `${apiBaseUrl}/papers/search?keyword=${encodeURIComponent(params.query)}&source=${encodeURIComponent(source)}&sort_by=${encodeURIComponent(sortBy)}&limit=${limit}`;
  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      return [];
    }
    const payload = (await response.json()) as { papers?: PaperItem[] };
    return payload.papers ?? [];
  } catch {
    return [];
  }
}

export async function fetchSocialBuzz(query: string, limit: number = 10): Promise<SocialItem[]> {
  if (!apiBaseUrl) {
    return [];
  }
  const url = `${apiBaseUrl}/social/search?keyword=${encodeURIComponent(query)}&limit=${limit}`;
  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      return [];
    }
    const payload = (await response.json()) as { posts?: SocialItem[] };
    return payload.posts ?? [];
  } catch {
    return [];
  }
}

export async function fetchLinkedInWatchlist(): Promise<LinkedInWatchlistItem[]> {
  if (!apiBaseUrl) {
    return [];
  }
  try {
    const response = await fetch(`${apiBaseUrl}/watchlists/linkedin`, { cache: "no-store" });
    if (!response.ok) {
      return [];
    }
    const payload = (await response.json()) as { items?: LinkedInWatchlistItem[] };
    return payload.items ?? [];
  } catch {
    return [];
  }
}

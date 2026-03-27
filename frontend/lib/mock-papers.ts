export type PaperRecord = {
  id: string;
  source_name: "openalex" | "semanticscholar";
  title: string;
  authors: string[];
  venue: string;
  year: number;
  abstract: string;
  cited_by_count: number;
  doi: string;
  url: string;
  latest_score: number;
  hot_score: number;
  influential_score: number;
  final_score: number;
  related_ids: string[];
};

export const MOCK_PAPERS: PaperRecord[] = [
  {
    id: "openalex:W1",
    source_name: "openalex",
    title: "Large Language Models for Biomedical Discovery",
    authors: ["Alice Zhang", "Leo Kim"],
    venue: "Nature Machine Intelligence",
    year: 2025,
    abstract:
      "This work explores large language model agents for literature-driven biomedical hypothesis generation and validation. We evaluate retrieval quality, evidence grounding, and experiment planning across multiple biomedical domains, and show improvements in hypothesis novelty and validation efficiency under expert review.",
    cited_by_count: 116,
    doi: "10.1038/s42256-025-00001-2",
    url: "https://example.org/paper-1",
    latest_score: 0.93,
    hot_score: 0.91,
    influential_score: 0.84,
    final_score: 0.9,
    related_ids: ["semanticscholar:S2", "openalex:W3"],
  },
  {
    id: "semanticscholar:S2",
    source_name: "semanticscholar",
    title: "Graph Retrieval-Augmented Generation for Science",
    authors: ["Mina Park", "Tom Rivera"],
    venue: "ICLR",
    year: 2024,
    abstract:
      "A retrieval-augmented framework combines graph-based indexing with language models for robust scientific question answering. The system links claims to evidence paths, improves faithfulness under adversarial prompts, and enables transparent attribution of reasoning steps.",
    cited_by_count: 203,
    doi: "10.48550/arXiv.2404.12345",
    url: "https://example.org/paper-2",
    latest_score: 0.86,
    hot_score: 0.89,
    influential_score: 0.9,
    final_score: 0.88,
    related_ids: ["openalex:W1", "semanticscholar:S4"],
  },
  {
    id: "openalex:W3",
    source_name: "openalex",
    title: "Efficient Multimodal Retrieval for Research Archives",
    authors: ["Ravi Patel", "Emma Chen", "Noah Silva"],
    venue: "ACL",
    year: 2023,
    abstract:
      "The paper presents an efficient multimodal indexing pipeline for text, tables, and figures in large research corpora. It introduces compression-aware fusion and adaptive reranking to reduce latency while preserving answer relevance in scholarly exploration workflows.",
    cited_by_count: 154,
    doi: "10.18653/v1/2023.acl-main.100",
    url: "https://example.org/paper-3",
    latest_score: 0.78,
    hot_score: 0.81,
    influential_score: 0.85,
    final_score: 0.81,
    related_ids: ["openalex:W1"],
  },
  {
    id: "semanticscholar:S4",
    source_name: "semanticscholar",
    title: "Benchmarking Scientific Search and Ranking Signals",
    authors: ["Olivia Martin", "Jinwoo Han"],
    venue: "KDD",
    year: 2022,
    abstract:
      "This benchmark analyzes freshness, citation dynamics, and venue prestige for scientific search ranking models. It provides reproducible tasks, robust metrics, and calibration guidelines for balancing recency and long-term influence in paper recommendation systems.",
    cited_by_count: 322,
    doi: "10.1145/3580305.3599301",
    url: "https://example.org/paper-4",
    latest_score: 0.7,
    hot_score: 0.79,
    influential_score: 0.95,
    final_score: 0.8,
    related_ids: ["semanticscholar:S2"],
  },
];

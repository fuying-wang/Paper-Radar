from __future__ import annotations

import re
from collections import Counter

from app.schemas.paper import Paper
from app.schemas.summary import PaperSummary, TrendSummary


STOPWORDS = {
    "the",
    "a",
    "an",
    "for",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "with",
    "by",
    "from",
    "using",
    "based",
    "towards",
    "via",
    "new",
    "study",
    "paper",
}

METHOD_TERMS = [
    "transformer",
    "retrieval",
    "graph",
    "benchmark",
    "diffusion",
    "agent",
    "prompt",
    "reranking",
    "multimodal",
    "reinforcement",
]


def _split_sentences(text: str) -> list[str]:
    parts = [item.strip() for item in re.split(r"[.!?]+", text) if item.strip()]
    return parts


def summarize_paper(paper: Paper) -> PaperSummary:
    sentences = _split_sentences(paper.abstract)
    research_problem = sentences[0] if len(sentences) >= 1 else f"This paper addresses {paper.title}."
    method = sentences[1] if len(sentences) >= 2 else f"The method is centered on {paper.title.lower()}."
    main_contribution = (
        sentences[2]
        if len(sentences) >= 3
        else f"The work contributes empirical evidence with {paper.cited_by_count} citations."
    )
    three_sentence_summary = f"{research_problem}. {method}. {main_contribution}."
    return PaperSummary(
        paper_id=paper.id,
        research_problem=research_problem,
        method=method,
        main_contribution=main_contribution,
        three_sentence_summary=three_sentence_summary,
    )


def summarize_papers(papers: list[Paper]) -> list[PaperSummary]:
    return [summarize_paper(paper) for paper in papers]


def _tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text)]
    return [token for token in tokens if token not in STOPWORDS]


def generate_trend_summary(papers: list[Paper], top_n: int = 3) -> TrendSummary:
    if not papers:
        return TrendSummary(hottest_directions=[], high_frequency_keywords=[], common_methods=[])

    hottest = sorted(papers, key=lambda item: (item.hot_score, item.final_score), reverse=True)[:top_n]
    hottest_directions = [paper.title for paper in hottest]

    keyword_counter: Counter[str] = Counter()
    for paper in papers:
        keyword_counter.update(_tokenize(f"{paper.title} {paper.abstract}"))
    high_frequency_keywords = [keyword for keyword, _ in keyword_counter.most_common(top_n)]

    method_counter: Counter[str] = Counter()
    for paper in papers:
        text = f"{paper.title} {paper.abstract}".lower()
        for term in METHOD_TERMS:
            if term in text:
                method_counter[term] += 1
    common_methods = [term for term, _ in method_counter.most_common(top_n)]

    return TrendSummary(
        hottest_directions=hottest_directions,
        high_frequency_keywords=high_frequency_keywords,
        common_methods=common_methods,
    )

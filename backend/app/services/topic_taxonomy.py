from __future__ import annotations

from dataclasses import dataclass


TOPIC_TAXONOMY: dict[str, dict[str, list[str]]] = {
    "Healthcare AI": {
        "medical imaging": ["medical imaging", "imaging", "x-ray", "mri", "ct", "ultrasound"],
        "ECG": ["ecg", "electrocardiogram"],
        "EHR": ["ehr", "electronic health record", "clinical notes"],
        "pathology": ["pathology", "histopathology", "whole slide image"],
        "radiology": ["radiology", "radiologist", "radiological"],
        "multimodal healthcare": ["multimodal healthcare", "clinical multimodal", "ehr imaging"],
        "medical foundation model": ["medical foundation model", "biomedical foundation model"],
        "medical reasoning": ["medical reasoning", "clinical reasoning"],
        "medical agent": ["medical agent", "clinical agent"],
    },
    "General AI": {
        "LLM": ["llm", "large language model"],
        "MLLM": ["mllm", "multimodal llm", "vision language model"],
        "reasoning": ["reasoning", "chain-of-thought", "cot"],
        "agent": ["agent", "autonomous agent", "agentic"],
        "RAG": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
        "alignment": ["alignment", "safety alignment", "value alignment"],
        "evaluation": ["evaluation", "benchmark", "leaderboard"],
        "multimodal foundation model": ["multimodal foundation model", "foundation model"],
    },
    "Crossovers": {
        "medical MLLM": ["medical mllm", "medical multimodal llm", "clinical vlm"],
        "clinical reasoning": ["clinical reasoning", "diagnostic reasoning"],
        "healthcare agent": ["healthcare agent", "clinical workflow agent"],
        "multimodal diagnosis": ["multimodal diagnosis", "diagnostic multimodal"],
        "foundation model adaptation for healthcare": [
            "healthcare adaptation",
            "clinical adaptation",
            "medical domain adaptation",
        ],
    },
}


@dataclass
class TopicClassification:
    primary_topic: str
    secondary_topics: list[str]
    matched_keywords: list[str]


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def classify_text_with_taxonomy(text: str) -> TopicClassification:
    normalized_text = _normalize_text(text)
    topic_scores: dict[str, int] = {}
    matched_secondary_topics: list[str] = []
    matched_keywords: list[str] = []

    for primary_topic, secondary_topic_mapping in TOPIC_TAXONOMY.items():
        for secondary_topic, keywords in secondary_topic_mapping.items():
            hit_count = 0
            for keyword in keywords:
                if keyword in normalized_text:
                    hit_count += 1
                    matched_keywords.append(keyword)
            if hit_count == 0:
                continue
            matched_secondary_topics.append(secondary_topic)
            topic_scores[primary_topic] = topic_scores.get(primary_topic, 0) + hit_count

    if not topic_scores:
        return TopicClassification(
            primary_topic="General AI",
            secondary_topics=[],
            matched_keywords=[],
        )

    if topic_scores.get("Crossovers", 0) > 0:
        primary_topic = "Crossovers"
    elif topic_scores.get("Healthcare AI", 0) > 0 and topic_scores.get("General AI", 0) > 0:
        primary_topic = "Crossovers"
    else:
        primary_topic = max(topic_scores.items(), key=lambda item: item[1])[0]
    dedup_secondary_topics = list(dict.fromkeys(matched_secondary_topics))
    dedup_keywords = list(dict.fromkeys(matched_keywords))
    return TopicClassification(
        primary_topic=primary_topic,
        secondary_topics=dedup_secondary_topics,
        matched_keywords=dedup_keywords,
    )

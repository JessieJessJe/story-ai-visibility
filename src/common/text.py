"""Utility helpers for manipulating transcript text."""

from __future__ import annotations

import re
from typing import Dict, Iterable

_WHITESPACE_RE = re.compile(r"\s+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def normalize_whitespace(value: str) -> str:
    """Collapse repeated whitespace and trim."""

    return _WHITESPACE_RE.sub(" ", value).strip()


def mask_terms(value: str, terms: Iterable[str], token: str = "<redacted>") -> str:
    """Replace sensitive terms in a case-insensitive fashion."""

    masked = value
    for term in terms:
        if not term:
            continue
        escaped = re.escape(term)
        masked = re.sub(escaped, token, masked, flags=re.IGNORECASE)
    return masked


def split_paragraphs(value: str) -> list[str]:
    """Split transcripts into cleaned paragraphs."""

    return [segment.strip() for segment in value.splitlines() if segment.strip()]


def strip_markup(value: str) -> str:
    """Remove basic HTML or markdown tags prior to normalization."""

    # Replace angle-bracket tags with whitespace to preserve separation.
    return _HTML_TAG_RE.sub(" ", value)


def keyword_hits(value: str, terms: Iterable[str]) -> Dict[str, int]:
    """Return a count of how many times each term appears case-insensitively."""

    lowered = value.lower()
    hits: Dict[str, int] = {}
    for term in terms:
        term = term.strip()
        if not term:
            continue
        count = lowered.count(term.lower())
        if count:
            hits[term] = count
    return hits


__all__ = ["normalize_whitespace", "mask_terms", "split_paragraphs", "strip_markup", "keyword_hits"]

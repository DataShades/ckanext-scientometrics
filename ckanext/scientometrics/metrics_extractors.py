from __future__ import annotations

import logging
from typing import Any

import requests
from pyalex import Authors
from scholarly import scholarly
from semanticscholar import SemanticScholar
from semanticscholar.SemanticScholarException import SemanticScholarException

log = logging.getLogger(__name__)


class AuthorMetricsExtractor:
    """Base class for extracting author metrics."""

    def extract_metrics(self, author_id: str) -> dict[str, Any]:
        """Method to be implemented by subclasses."""
        raise NotImplementedError


class GoogleScholarAuthorMetricsExtractor(AuthorMetricsExtractor):
    """Extracts author metrics from Google Scholar."""

    def extract_metrics(self, author_id: str) -> dict[str, Any]:
        try:
            author = scholarly.search_author_id(author_id)
            author = scholarly.fill(author, sections=["indices"])
        except AttributeError:
            log.exception("Google Scholar could not find the author")
            return {}
        return {
            "h_index": author["hindex"],
            "h_index_5y": author["hindex5y"],
            "i10_index": author["i10index"],
            "i10_index_5y": author["i10index5y"],
            "citation_count": author["citedby"],
            "citation_count_5y": author["citedby5y"],
        }


class SemanticScholarAuthorMetricsExtractor(AuthorMetricsExtractor):
    """Extracts author metrics from Semantic Scholar."""

    def extract_metrics(self, author_id: str) -> dict[str, Any]:
        sch = SemanticScholar()
        try:
            author = sch.get_author(author_id)
        except SemanticScholarException:
            log.exception("Semantic Scholar could not find the author")
            return {}
        return {
            "h_index": author.hIndex,
            "citation_count": author.citationCount,
            "paper_count": author.paperCount,
        }


class OpenAlexAuthorMetricsExtractor(AuthorMetricsExtractor):
    """Extracts author metrics from OpenAlex."""

    def extract_metrics(self, author_id: str) -> dict[str, Any]:
        try:
            author = Authors()[author_id]
        except requests.exceptions.HTTPError:
            log.exception("OpenAlex could not find the author")
            return {}
        return {
            "h_index": author["summary_stats"]["h_index"],
            "i10_index": author["summary_stats"]["i10_index"],
            "citation_count": author["cited_by_count"],
            "paper_count": author["works_count"],
        }

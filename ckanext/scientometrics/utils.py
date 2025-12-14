from __future__ import annotations

import logging
from typing import Any

import ckan.plugins as p

from ckanext.scientometrics.interfaces import IScientometrics
from ckanext.scientometrics.metrics_extractors import (
    AuthorMetricsExtractor,
    GoogleScholarAuthorMetricsExtractor,
    OpenAlexAuthorMetricsExtractor,
    SemanticScholarAuthorMetricsExtractor,
)

log = logging.getLogger(__name__)


def get_metrics_extractor(source: str) -> AuthorMetricsExtractor:
    extractors = {
        "google_scholar_author": GoogleScholarAuthorMetricsExtractor,
        "semantic_scholar_author": SemanticScholarAuthorMetricsExtractor,
        "openalex_author": OpenAlexAuthorMetricsExtractor,
    }
    for plugin in p.PluginImplementations(IScientometrics):
        custom = plugin.get_metrics_extractors() or {}
        if custom:
            extractors.update(custom)
            break
    if source not in extractors:
        raise ValueError
    return extractors[source]()


def fetch_author_metrics(source: str, author_id: str) -> dict[str, Any]:
    """Fetch author metrics from the given source using the unified extractor."""
    extractor = get_metrics_extractor(source)
    return extractor.extract_metrics(author_id)

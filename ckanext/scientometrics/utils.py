from __future__ import annotations

import logging
from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.scientometrics import const
from ckanext.scientometrics.interfaces import IScientometrics
from ckanext.scientometrics.metrics_extractors import (
    AuthorMetricsExtractor,
    GoogleScholarAuthorMetricsExtractor,
    OpenAlexAuthorMetricsExtractor,
    SemanticScholarAuthorMetricsExtractor,
)

log = logging.getLogger(__name__)


def get_metrics_extractor(source: str) -> AuthorMetricsExtractor:
    for plugin in p.PluginImplementations(IScientometrics):
        extractors = plugin.get_metrics_extractors()
        break
    else:
        extractors = {
            "google_scholar_author": GoogleScholarAuthorMetricsExtractor,
            "semantic_scholar_author": SemanticScholarAuthorMetricsExtractor,
            "openalex_author": OpenAlexAuthorMetricsExtractor,
        }
    if source not in extractors:
        raise ValueError(f"Unsupported source: {source}")
    return extractors[source]()


def fetch_author_metrics(source: str, author_id: str) -> dict[str, Any]:
    """Fetch author metrics from the given source using the unified extractor."""
    extractor = get_metrics_extractor(source)
    return extractor.extract_metrics(author_id)


def save_metrics_in_flake(
        user_id: str, metrics_type: str, author_id: str | int, metrics: dict[str, Any]
) -> None:
    """Save the metrics in the flake."""
    flake = get_data_from_flake(const.FLAKE_METRICS.format(user_id))
    flake["data"][metrics_type] = metrics
    flake["data"][metrics_type]["author_id"] = author_id
    store_data_in_flake(const.FLAKE_METRICS.format(user_id), flake["data"])


def get_metrics_from_flake(user_id: str) -> dict[str, Any]:
    """Retrieve the metrics from the flake."""
    return get_data_from_flake(const.FLAKE_METRICS.format(user_id))["data"]


def store_data_in_flake(flake_name: str, data: Any) -> dict[str, Any]:
    """Save the serializable data into the flakes table."""
    return tk.get_action("flakes_flake_override")(
        {"ignore_auth": True},
        {"author_id": None, "name": flake_name, "data": data},
    )


def get_data_from_flake(flake_name: str) -> dict[str, Any]:
    """Retrieve a previously stored data from the flake."""
    try:
        return tk.get_action("flakes_flake_lookup")(
            {"ignore_auth": True},
            {"author_id": None, "name": flake_name},
        )
    except tk.ObjectNotFound:
        return tk.get_action("flakes_flake_create")(
            {"ignore_auth": True},
            {"author_id": None, "name": flake_name, "data": {}},
        )

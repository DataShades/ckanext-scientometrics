from __future__ import annotations

from ckan.plugins.interfaces import Interface

from ckanext.scientometrics.metrics_extractors import AuthorMetricsExtractor


class IScientometrics(Interface):
    def get_metrics_extractors(self) -> dict[str, type[AuthorMetricsExtractor]]:
        """Allows to redefine the default metrics extractors.

        Default:
        extractors = {
            "google_scholar_author": GoogleScholarAuthorMetricsExtractor,
            "semantic_scholar_author": SemanticScholarAuthorMetricsExtractor,
            "openalex_author": OpenAlexAuthorMetricsExtractor,
        }
        """
        return {}

from __future__ import annotations

import ckan.plugins.toolkit as tk

CONFIG_ENABLED_METRICS = "ckanext.scientometrics.enabled_metrics"
CONFIG_SHOW_ON_USER_PAGE = "ckanext.scientometrics.show_on_user_page"


def enabled_metrics() -> list[str]:
    """List of enabled metrics."""
    return tk.config[CONFIG_ENABLED_METRICS]


def show_metrics_on_user_page() -> bool:
    """Show metrics on user page in the info section."""
    return tk.config[CONFIG_SHOW_ON_USER_PAGE]

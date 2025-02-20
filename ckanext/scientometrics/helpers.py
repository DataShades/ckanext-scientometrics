from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk

from ckanext.scientometrics import config


def scientometrics_get_user_metrics(user_id: str) -> dict[str, Any]:
    """Retrieve the metrics for a user."""
    return tk.get_action("scientometrics_get_user_metrics")({}, {"user_id": user_id})


def scientometrics_get_enabled_metrics() -> list[str]:
    """List of enabled metrics."""
    return config.enabled_metrics()


def scientometrics_show_metrics_on_user_page() -> bool:
    """Show metrics on user page in the info section."""
    return config.show_metrics_on_user_page()

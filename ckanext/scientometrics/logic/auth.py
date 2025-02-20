from __future__ import annotations

from typing import Any

from ckan import authz, types


def scientometrics_update_user_metrics(
    context: types.Context, data_dict: dict[str, Any]
):
    return authz.is_authorized("sysadmin", context, data_dict)

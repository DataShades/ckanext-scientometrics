from __future__ import annotations

from typing import Any

from ckan import types


def scim_update_user_metrics(context: types.Context, data_dict: dict[str, Any]):
    return {"success": False}


def scim_get_user_metrics(context: types.Context, data_dict: dict[str, Any]):
    return {"success": True}


def scim_delete_user_metrics(context: types.Context, data_dict: dict[str, Any]):
    return {"success": False}

from __future__ import annotations

import copy
import logging
from typing import Any

import ckan.plugins.toolkit as tk
from ckan import model, types
from ckan.logic import validate

from ckanext.scientometrics import config, utils
from ckanext.scientometrics.logic import schema
from ckanext.scientometrics.model import UserMetric

log = logging.getLogger(__name__)


@tk.chained_action
def user_update(next_: Any, context: types.Context, data_dict: dict[str, Any]):
    """Attach scientometrics extras to a user when it is updated."""
    user = next_(context, data_dict)
    _attach_extras(context, data_dict, user["id"])
    return user


@tk.chained_action
@tk.side_effect_free
def user_show(next_: Any, context: types.Context, data_dict: dict[str, Any]):
    """Retrieve a user's scientometrics extras."""
    user_data = next_(context, data_dict)

    userobj = context["model"].User.get(user_data["id"])
    if not userobj:
        raise tk.ObjectNotFound("user")
    if userobj.plugin_extras and "scim" in userobj.plugin_extras:
        user_data["scim"] = copy.deepcopy(userobj.plugin_extras.get("scim", {}))
    return user_data


def _attach_extras(context: types.Context, data_dict: dict[str, Any], user_id: str):
    sm_details, _ = tk.navl_validate(data_dict, schema.user_extras(), context)

    sm_details.pop("__extras", None)
    userobj = context["model"].User.get(user_id)
    if not userobj:
        raise tk.ObjectNotFound("user")
    extras = copy.deepcopy(userobj.plugin_extras or {})

    scim = extras.setdefault("scim", {})
    for source in config.enabled_metrics():
        key = f"{source}_author_id"
        if key in data_dict and not data_dict.get(key):
            scim.pop(key, None)
    scim.update(sm_details)
    userobj.plugin_extras = extras
    userobj.save()


@tk.side_effect_free
@validate(schema.scim_update_user_metrics)
def scim_get_user_metrics(context: types.Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Retrieve user scientometrics metrics.

    Args:
        context (Dict[str, Any]): The CKAN action context.
        data_dict (Dict[str, Any]): A dictionary containing:
            - "user_id": The ID of the user whose metrics we want to retrieve.

    Returns:
        Dict[str, Any]: The user's scientometrics metrics keyed by source.
    """
    user_id_or_name = data_dict["user_id"]

    user_dict = tk.get_action("user_show")({"ignore_auth": True}, {"id": user_id_or_name})
    records = UserMetric.by_user_id(user_dict["id"])
    return {record.source: record.dictize({}) for record in records}


@validate(schema.scim_update_user_metrics)
def scim_update_user_metrics(context: types.Context, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Create/update a user's scientometrics metrics using author ids.

    Args:
        context (Context): The CKAN action context.
        data_dict (dict[str, Any]): A dictionary containing:
            - "user_id": The ID of the user to update.
            - "requested_sources": A list or dict indicating which metrics to update (subset of extras).

    Returns:
        Dict[str, Any]: A dictionary containing the updated metrics.
    """
    tk.check_access("scim_update_user_metrics", context, data_dict)
    user_id_or_name = data_dict["user_id"]
    user_dict = tk.get_action("user_show")({"ignore_auth": True}, {"id": user_id_or_name})
    user_id = user_dict["id"]

    requested_sources = set(data_dict["requested_sources"] or [])
    records = UserMetric.by_user_id(user_id)
    existing = {record.source: record for record in records}
    authors = _collect_authors(user_id, existing)
    sources = requested_sources & set(authors.keys()) if requested_sources else set(authors.keys())
    updated_metrics: dict[str, dict[str, Any]] = {}

    for source in sources:
        author_id = authors.get(source)
        if not author_id:
            continue

        try:
            extracted_metrics = utils.fetch_author_metrics(source + "_author", author_id)
        except tk.ValidationError as exc:
            log.warning("Failed to fetch metrics for user %s source %s: %s", user_id, source, exc, exc_info=True)
            extracted_metrics = {"error": str(exc)}
        if not extracted_metrics:
            continue

        payload = dict(extracted_metrics)
        payload["author_id"] = author_id
        existing_record = existing.get(source)
        external_id = payload.get("external_id") or (existing_record.external_id if existing_record else str(author_id))
        external_url = (
            payload.get("external_url")
            or payload.get("url")
            or (existing_record.external_url if existing_record else None)
        )
        status = existing_record.status if existing_record else "pending"
        external = {"id": external_id, "url": external_url}

        UserMetric.upsert(
            user_id=user_id,
            source=source,
            metrics=payload,
            external=external,
            status=status,
        )
        updated_metrics[source] = extracted_metrics

    model.Session.commit()

    return updated_metrics


@validate(schema.scim_delete_user_metrics)
def scim_delete_user_metrics(context: types.Context, data_dict: dict[str, Any]) -> int:
    """Delete all scientometrics metrics for a user."""
    tk.check_access("scim_delete_user_metrics", context, data_dict)
    user_dict = tk.get_action("user_show")({"ignore_auth": True}, {"id": data_dict["user_id"]})
    deleted = UserMetric.delete_by_user_id(user_dict["id"])
    model.Session.commit()
    return deleted


def _collect_authors(user_id: str, existing: dict[str, UserMetric]) -> dict[str, str]:
    """Collect authors strictly from user extras (scim or legacy scientometrics)."""
    authors: dict[str, str] = {}
    user_obj = model.User.get(user_id)
    extras = (user_obj.plugin_extras or {}) if user_obj else {}
    scim_extras = extras.get("scim") or extras.get("scientometrics") or {}
    for key, val in scim_extras.items():
        if key.endswith("_author_id") and val:
            authors[key.removesuffix("_author_id")] = val
    return authors

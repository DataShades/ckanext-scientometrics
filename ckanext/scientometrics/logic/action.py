from __future__ import annotations

import copy
from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic import validate

from ckanext.scientometrics import utils
from ckanext.scientometrics.logic import schema


@tk.chained_action
def user_create(next_: Any, context: types.Context, data_dict: dict[str, Any]):
    """Attach scientometrics extras to a user when it is created."""
    user = next_(context, data_dict)
    _attach_extras(context, data_dict, user["id"])
    return user


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
    if userobj.plugin_extras and "scientometrics" in userobj.plugin_extras:
        user_data["scientometrics"] = copy.deepcopy(
            userobj.plugin_extras.get("scientometrics", {})
        )
    return user_data


def _attach_extras(context: types.Context, data_dict: dict[str, Any], user_id: str):
    sm_details, _ = tk.navl_validate(data_dict, schema.user_extras(), context)

    sm_details.pop("__extras", None)
    userobj = context["model"].User.get(user_id)
    if not userobj:
        raise tk.ObjectNotFound("user")
    extras = copy.deepcopy(userobj.plugin_extras or {})

    if "scientometrics" not in extras:
        extras["scientometrics"] = {}
    extras["scientometrics"].update(sm_details)
    userobj.plugin_extras = extras
    userobj.save()


@tk.side_effect_free
@validate(schema.scientometrics_update_user_metrics)
def scientometrics_update_user_metrics(
        context: types.Context, data_dict: dict[str, Any]
) -> dict[str, Any]:
    """Update a user's scientometrics metrics.

    Args:
        context (Context): The CKAN action context.
        data_dict (dict[str, Any]): A dictionary containing:
            - "user_id": The ID of the user to update.
            - "requested_sources": A list or dict indicating which metrics to update.

    Returns:
        Dict[str, Any]: A dictionary containing the updated metrics.
    """
    user_id_or_name = data_dict["user_id"]
    user_dict = tk.get_action("user_show")(
        {"ignore_auth": True}, {"id": user_id_or_name}
    )
    user_id = user_dict["id"]

    requested_sources = data_dict["requested_sources"]
    scientometrics_ids = user_dict.get("scientometrics", {})
    updated_metrics = {}

    for metric_id_key, author_id in scientometrics_ids.items():
        source = metric_id_key.replace("_author_id", "")
        if not source or source not in requested_sources:
            continue

        extracted_metrics = utils.fetch_author_metrics(source + "_author", author_id)
        if not extracted_metrics:
            continue

        utils.save_metrics_in_flake(user_id, source, author_id, extracted_metrics)
        updated_metrics[source] = extracted_metrics

    return updated_metrics


@tk.side_effect_free
@validate(schema.scientometrics_update_user_metrics)
def scientometrics_get_user_metrics(
        context: types.Context, data_dict: dict[str, Any]
) -> dict[str, Any]:
    """Retrieve user scientometrics metrics.

    Args:
        context (Dict[str, Any]): The CKAN action context.
        data_dict (Dict[str, Any]): A dictionary containing:
            - "user_id": The ID of the user whose metrics we want to retrieve.

    Returns:
        Dict[str, Any]: The user's scientometrics metrics from the flake store.
    """
    user_id_or_name = data_dict["user_id"]

    user_dict = tk.get_action("user_show")(
        {"ignore_auth": True}, {"id": user_id_or_name}
    )

    return utils.get_metrics_from_flake(user_dict["id"])

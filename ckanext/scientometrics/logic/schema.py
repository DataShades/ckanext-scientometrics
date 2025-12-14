from ckan import types
from ckan.logic.schema import validator_args

from ckanext.scientometrics import config


@validator_args
def user_extras(ignore_empty: types.Validator) -> types.Schema:
    return {source + "_author_id": [ignore_empty] for source in config.enabled_metrics()}


@validator_args
def scim_update_user_metrics(
    not_empty: types.Validator,
    default: types.Validator,
    convert_to_list_if_string: types.Validator,
) -> types.Schema:
    return {
        "user_id": [not_empty],
        "requested_sources": [
            default(config.enabled_metrics()),
            convert_to_list_if_string,
        ],
    }


@validator_args
def scim_delete_user_metrics(
    not_empty: types.Validator,
) -> types.Schema:
    return {
        "user_id": [not_empty],
    }

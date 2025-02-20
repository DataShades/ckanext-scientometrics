import click

import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.scientometrics import config

__all__ = [
    "scientometrics",
]


@click.group()
def scientometrics():
    pass


@scientometrics.command()
@click.option(
    "--user-ids",
    type=str,
    default=(),
    multiple=True,
    help="The user ID to update the metrics for.",
)
@click.option(
    "--requested-sources",
    type=str,
    default=(),
    multiple=True,
    help="The sources to update the metrics for.",
)
def update_user_metrics(user_ids: tuple, requested_sources: tuple):
    """Update the metrics for all users.

    If a user_ids is provided, only update the metrics for those users.
    If requested_sources is provided, only update the metrics for those sources.
    """
    if not user_ids:
        user_ids = [user.id for user in model.User.all()]

    if not requested_sources:
        requested_sources = config.enabled_metrics()
    with click.progressbar(user_ids, label="Updating user metrics") as bar:
        for user_id in bar:
            tk.get_action("scientometrics_update_user_metrics")(
                {}, {"user_id": user_id, "requested_sources": requested_sources}
            )

    click.echo("Metrics update complete!")

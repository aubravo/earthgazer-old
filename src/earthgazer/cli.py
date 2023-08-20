"""
Module that contains the command line app.
"""
import logging

import click

from earthgazer import __version__
from earthgazer.eg import EGProcessor
from click_aliases import ClickAliasedGroup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option("-v", "--version", is_flag=True, help="Prints the current version.")
@click.option("-d", "--debug", is_flag=True, help="Prints the current version.")
@click.pass_context
def main(ctx, version, debug):
    ctx.ensure_object(dict)
    if version:
        click.echo(__version__)
        return
    if debug:
        logger.setLevel(logging.DEBUG)
        ctx.obj["DEBUG"] = True


@main.group(cls=ClickAliasedGroup)
def locations():
    """
    Location commands.
    """


@locations.command(help="List locations.", aliases=["ls", "list"])
@click.pass_context
def records(ctx):
    eg = EGProcessor()
    click.echo(f"  ID | {'Location Name':25} | {'Latitude':>11} | {'Longitude':>11} | {'status':>8} | {'Start':10} | {'End':10}")
    for _ in eg.list_locations():
        click.echo(_)


@locations.command(help="Add location.", aliases=["create", "new", "mk", "make"])
@click.argument("location_name")
@click.argument("latitude", type=float)
@click.argument("longitude", type=float)
@click.option("--from", "from_date", type=click.DateTime())
@click.option("--to", "to_date", type=click.DateTime())
@click.pass_context
def add(ctx, location_name, latitude, longitude, from_date, to_date):
    eg = EGProcessor()
    eg.add_location(
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        monitoring_period_start=from_date,
        monitoring_period_end=to_date,
    )


@locations.command(help="Remove location.", aliases=["rm", "delete"])
@click.argument("location_id")
@click.pass_context
def drop(ctx, location_id):
    eg = EGProcessor()
    eg.drop_location(location_id)


@main.group(cls=ClickAliasedGroup)
def pipeline():
    """
    Pipeline commands.
    """

@pipeline.command(help="Query bigquery to get metadata for all images in a location.", aliases=["bigquery", "update-data"])
@click.pass_context
def update_bigquery_data(ctx):
    logger.setLevel(logging.DEBUG)
    eg = EGProcessor()
    eg.update_bigquery_data()

@pipeline.command(help="Analyze image location and extract metadata before confirming loading.", aliases=["analyze", "extract"])
@click.pass_context
def get_source_file_data(ctx):
    eg = EGProcessor()
    eg.get_source_file_data()


@pipeline.command(help="Backup missing images into storage filesystem.", aliases=["load", "download"])
@click.pass_context
def backup_images(ctx):
    eg = EGProcessor()
    eg.backup_images()

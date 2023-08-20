"""
Module that contains the command line app.
"""
import click

from earthgazer import __version__
from earthgazer.eg import EGProcessor


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
        ctx.obj["DEBUG"] = True


@main.group()
def locations():
    """
    Location commands.
    """


@locations.command(help="List locations.")
@click.pass_context
def list(ctx):
    eg = EGProcessor()
    click.echo(f"  ID | {'Location Name':25} | {'Latitude':>11} | {'Longitude':>11} | {'status':>8} | {'Start':10} | {'End':10}")
    for _ in eg.list_locations():
        click.echo(_)


@locations.command(help="Add location.")
@click.argument("location_name")
@click.argument("latitude", type=float)
@click.argument("longitude", type=float)
@click.option("--from", "from_date", type=click.DateTime())
@click.option("--to", "to_date", type=click.DateTime())
@click.pass_context
def add(ctx, location_name, latitude, longitude, from_date, to_date):
    eg = EGProcessor()
    eg.add_location(
        **{
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "monitoring_period_start": from_date,
            "monitoring_period_end": to_date,
        }
    )


@locations.command(help="Remove location.")
@click.argument("location_id")
@click.pass_context
def drop(ctx, location_id):
    eg = EGProcessor()
    eg.drop_location(location_id)

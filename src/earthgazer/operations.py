from pathlib import Path

import jinja2

from earthgazer.location import Location
from earthgazer.platforms import Platform


def render_bigquery_template(platform: Platform, location: Location):
    queries_dir = Path(__file__).parent.parent / "queries"
    sql_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(queries_dir, encoding="utf-8"), autoescape=True)
    mappings = {}
    mappings.update(platform.bigquery_attribute_mapping)
    mappings.update(location.as_dict)
    return sql_environment.get_template("bigquery_get_locations.sql").render(**mappings)

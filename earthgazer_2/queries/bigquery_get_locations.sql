SELECT
    {{ main_id }} AS main_id, {{ secondary_id }} AS secondary_id, {{ mission_id }} AS mission_id, {{ sensing_time }} AS sensing_time, {{ cloud_cover }} AS cloud_cover, {{ north_lat }} AS north_lat, {{ south_lat }} AS south_lat, {{ west_lon }} AS west_lon, {{ east_lon }} AS east_lon, {{ base_url }} AS base_url
FROM {{ bigquery_path }}
WHERE
    {{ sensing_time }} >= '{{ start_date }}' AND
    {{ sensing_time }} <= '{{ end_date }}' AND
    {{ north_lat }} >= {{ lat }} AND
    {{ south_lat }} <= {{ lat }} AND
    {{ west_lon }} <= {{ lon }} AND
    {{ east_lon }} >= {{ lon }}
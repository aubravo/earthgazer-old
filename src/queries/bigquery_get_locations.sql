SELECT
    {{ main_id | safe }} AS main_id,
    {{ secondary_id | safe }} AS secondary_id,
    {{ mission_id | safe }} AS mission_id,
    {{ sensing_time | safe }} AS sensing_time,
    {{ cloud_cover | safe }} AS cloud_cover,
    {{ north_lat | safe }} AS north_lat,
    {{ south_lat | safe }} AS south_lat,
    {{ west_lon | safe }} AS west_lon,
    {{ east_lon | safe }} AS east_lon,
    {{ base_url | safe }} AS base_url,
    {{ mgrs_tile | safe }} AS mgrs_tile,
    {{ wrs_path | safe }} AS wrs_path,
    {{ wrs_row | safe }} AS wrs_row,
    {{ data_type | safe }} AS data_type
FROM {{ bigquery_path }}
WHERE
    {{ sensing_time }} >= '{{ start_date }}' AND
    {{ sensing_time }} <= '{{ end_date }}' AND
    {{ extra_filters | safe }} AND
    {{ north_lat }} >= {{ lat }} AND
    {{ south_lat }} <= {{ lat }} AND
    {{ west_lon }} <= {{ lon }} AND
    {{ east_lon }} >= {{ lon }}

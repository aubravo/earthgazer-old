""" --- BIG QUERY --- """

landsat_bigquery = """
SELECT product_id, sensing_time, north_lat, south_lat, west_lon, east_lon, base_url
FROM bigquery-public-data.cloud_storage_geo_index.landsat_index
WHERE
spacecraft_id = "LANDSAT_8" AND
north_lat > 19.023463 AND
south_lat < 19.023463 AND
east_lon > -98.622686 AND
west_lon < -98.622686 AND
date_acquired >= "{}"
ORDER BY sensing_time ASC;
"""

sentinel_bigquery = """
SELECT granule_id, product_id, sensing_time, north_lat, south_lat, west_lon, east_lon, base_url
FROM bigquery-public-data.cloud_storage_geo_index.sentinel_2_index
WHERE
granule_id LIKE "L1C%" AND
north_lat > 19.023463 AND
south_lat < 19.023463 AND
east_lon > -98.622686 AND
west_lon < -98.622686 AND
sensing_time >= "{}"
ORDER BY sensing_time ASC;
"""

""" --- SQL --- """


landsat_insert = """
INSERT INTO gxiba.landsat (landsat_id, sensing_time, north_lat, south_lat, west_lon, east_lon, base_url, status)
VALUES (%(landsat_id)s, %(sensing_time)s, %(north_lat)s, %(south_lat)s, %(west_lon)s, %(east_lon)s, %(base_url)s,
%(status)s);
"""

landsat_create_table = """
CREATE TABLE IF NOT EXISTS gxiba.landsat (
    landsat_id VARCHAR(50) PRIMARY KEY,
    sensing_time TIMESTAMP,
    north_lat NUMERIC,
    south_lat NUMERIC,
    west_lon NUMERIC,
    east_lon NUMERIC,
    status VARCHAR(50),
    base_url VARCHAR(100)
);
"""

sentinel_insert = """
INSERT INTO gxiba.sentinel (sentinel_id, product, sensing_time, north_lat, south_lat, west_lon, east_lon, base_url, status)
VALUES (%(sentinel_id)s, %(product)s, %(sensing_time)s, %(north_lat)s, %(south_lat)s, %(west_lon)s, %(east_lon)s, %(base_url)s, %(status)s);
"""

sentinel_create_table = """
CREATE TABLE IF NOT EXISTS gxiba.sentinel (
    sentinel_id VARCHAR(50) PRIMARY KEY,
    product VARCHAR(50),
    sensing_time TIMESTAMP,
    north_lat NUMERIC,
    south_lat NUMERIC,
    west_lon NUMERIC,
    east_lon NUMERIC,
    status VARCHAR(50),
    base_url VARCHAR(100)
);
"""

landsat_get_most_recent_date = """
SELECT sensing_time FROM gxiba.landsat
ORDER BY sensing_time DESC
LIMIT 1;
"""

sentinel_get_most_recent_date = """
SELECT sensing_time FROM gxiba.sentinel
ORDER BY sensing_time DESC
LIMIT 1;
"""

landsat_get_queried = """
SELECT landsat_id, base_url
FROM gxiba.landsat
WHERE
status LIKE 'QUERIED'
"""

landsat_change_status = """
UPDATE gxiba.landsat
SET status = 'SYNCED'
WHERE landsat_id = '{}'
"""

sentinel_get_queried = """
SELECT sentinel_id, base_url
FROM gxiba.sentinel
WHERE
status LIKE 'QUERIED'
"""

sentinel_change_status = """
UPDATE gxiba.sentinel
SET status = 'SYNCED'
WHERE sentinel_id = '{}'
"""
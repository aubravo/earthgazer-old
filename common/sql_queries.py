landsat_bigquery = """
SELECT product_id, sensing_time, north_lat, south_lat, west_lon, east_lon, base_url
FROM bigquery-public-data.cloud_storage_geo_index.landsat_index
WHERE
spacecraft_id = "LANDSAT_8" AND
north_lat > 19.023463 AND
south_lat < 19.023463 AND
east_lon > -98.622686 AND
west_lon < -98.622686 AND
date_acquired > '2010-01-01'
"""

landsat_insert_query = """
INSERT INTO landsat (landsat_id, sensing_time, north_lat, south_lat, west_lon, east_lon, base_url, status)
VALUES (:landsat_id, :sensing_time, :north_lat, :south_lat, :west_lon, :east_lon, :base_url, :status);
"""

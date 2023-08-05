SELECT SUBSTR(secondary_id, -2) AS type, COUNT(*) FROM image_metadata
WHERE mission_id = 'LANDSAT_8',
GROUP BY type;
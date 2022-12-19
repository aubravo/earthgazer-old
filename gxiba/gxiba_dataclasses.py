from dataclasses import dataclass
from gxiba import DataBaseManager


class DuplicateGxibaMetadataRegistries(BaseException):
    ...


class GxibaMetadataRegistryNotFound(BaseException):
    ...


@dataclass
class GxibaImageMetadata:
    platform: str
    platform_id: str
    sensing_time: str
    latitude_north: float
    latitude_south: float
    longitude_west: float
    longitude_east: float
    base_url: str
    status: str

    def push_to_database(self, database_manager: DataBaseManager) -> None:
        result = database_manager.query(f"""SELECT * FROM gxiba_images
                WHERE platform_id LIKE "{self.platform_id}";""")
        if len(result) >= 1:
            raise DuplicateGxibaMetadataRegistries("Image metadata already present. Try update_database() instead")
        insert_query = f"""INSERT INTO gxiba_images
(platform, platform_id, sensing_time, latitude_north, latitude_south, longitude_east,longitude_west, base_url, status)
VALUES ("{self.platform}", "{self.platform_id}", "{self.sensing_time}", {self.latitude_north}, {self.latitude_south},
{self.longitude_west}, {self.longitude_east}, "{self.base_url}", "{self.status}");"""
        database_manager.execute(insert_query)

    def update_database(self, database_manager: DataBaseManager) -> None:
        result = database_manager.query(f"""SELECT * FROM gxiba_images
                WHERE platform_id LIKE "{self.platform_id}";""")
        if len(result) > 1:
            raise DuplicateGxibaMetadataRegistries("Duplicate image metadata found in database")
        elif len(result) <= 0:
            raise GxibaMetadataRegistryNotFound("Image metadata not found in database")
        update_query = f""" UPDATE gxiba_images SET
                        platform = "{self.platform}",
                        sensing_time = "{self.sensing_time}",
                        latitude_north = {self.latitude_north},
                        latitude_south = {self.latitude_south},
                        longitude_west = {self.longitude_west},
                        longitude_east = {self.longitude_east},
                        base_url = "{self.base_url}",
                        status = "{self.status}"
                        WHERE platform_id LIKE "{self.platform_id}";"""
        database_manager.execute(update_query)

    @staticmethod
    def get_from_platform_id(platform_id: str, database_manager: DataBaseManager):
        result = database_manager.query(f"""SELECT * FROM gxiba_images
        WHERE platform_id LIKE "{platform_id}";""")
        if len(result) > 1:
            raise DuplicateGxibaMetadataRegistries("Duplicate image metadata found in database")
        elif len(result) <= 0:
            raise GxibaMetadataRegistryNotFound("Image metadata not found in database")
        return GxibaImageMetadata(
                    platform=result['platform'][0],
                    platform_id=result['platform_id'][0],
                    sensing_time=result['sensing_time'][0],
                    latitude_north=result['latitude_north'][0],
                    latitude_south=result['latitude_south'][0],
                    longitude_west=result['longitude_west'][0],
                    longitude_east=result['longitude_east'][0],
                    base_url=result['base_url'][0],
                    status=result['status'][0])

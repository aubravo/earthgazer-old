from gxiba.storage_manager import LocalStorageManager, CloudStorageManager
from gxiba.storage_manager.google_cloud_storage_interface import GoogleCloudStorageInterface
from gxiba.image_processor import ImageProcessor
from gxiba.database_manager import DataBaseManager
from gxiba.database_manager.sqllite_engine import SQLiteDataBaseEngine
from gxiba.database_manager.postgres_engine import PostgresDataBaseEngine


if __name__ == "__main__":
    print("WELCOME TO GXIBA!")

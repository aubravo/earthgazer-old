from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from earthgazer.settings import EarthGazerSettings

Base = declarative_base()


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(str(EarthGazerSettings().database_manager.url))  # type: ignore
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

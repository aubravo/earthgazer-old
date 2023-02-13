from sqlalchemy import create_engine, URL
import earthgazer.setup

GXIBA_DATABASE_URL = URL.create(**earthgazer.setup.GXIBA_CONFIGURATION.database.dict())
GXIBA_DATABASE_ENGINE = create_engine(GXIBA_DATABASE_URL, echo=False, future=True)

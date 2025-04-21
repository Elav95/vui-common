from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from vui_common.configs.config_proxy import config_app
from vui_common.logger.logger_proxy import logger
from vui_common.database.base import Base

# ### added in common
BASE_DIR = Path.cwd()
DB_REL_PATH = config_app.database.database_path
DB_PATH = (BASE_DIR / DB_REL_PATH).resolve()
DATABASE_URL = f"sqlite:///{DB_PATH}/data.db"
# ###

# Log DB path
logger.info(f"Users database {DATABASE_URL}")

# Import models only to register them with Base
import vui_common.models.db.user  # noqa
import vui_common.models.db.project_versions  # noqa
import vui_common.models.db.refresh_token  # noqa

# SQLite engine setup
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False}
)

# Create tables
Base.metadata.create_all(bind=engine)

# DB session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Get DB for User CRUD operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

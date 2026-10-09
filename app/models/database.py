from sqlalchemy import create_engine
from config.runtime import APP_DIR
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_PATH = APP_DIR / "database" / "catalog.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
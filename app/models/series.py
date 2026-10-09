from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from app.models.database import Base

class Series(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    genre = Column(String)

    overview = Column(Text)

    poster_path = Column(String)

    tmdb_id = Column(Integer)
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Boolean

from app.models.database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    year = Column(Integer)

    director = Column(String)

    genre = Column(String)

    overview = Column(Text)

    runtime = Column(Integer)

    poster_path = Column(String)

    video_path = Column(String)

    tmdb_id = Column(Integer)

    favorite = Column(Boolean, default=False)

    watched = Column(Boolean, default=False, nullable=False)
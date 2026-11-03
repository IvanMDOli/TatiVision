from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Boolean

from app.models.database import Base

class Series(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    genre = Column(String)

    overview = Column(Text)

    poster_path = Column(String)

    tmdb_id = Column(Integer)

    year = Column(Integer)

    runtime = Column(Integer)

    director = Column(String)

    favorite = Column(Boolean, default=False, nullable=False)

    watched = Column(Boolean, default=False, nullable=False)

    cast_members = Column(Text)
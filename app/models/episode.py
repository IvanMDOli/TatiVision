from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.models.database import Base

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True)

    series_id = Column(Integer)

    season = Column(Integer)

    episode = Column(Integer)

    title = Column(String)

    video_path = Column(String)
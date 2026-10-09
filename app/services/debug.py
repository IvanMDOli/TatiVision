from app.models.database import SessionLocal
from app.models.movie import Movie

session = SessionLocal()

movies = session.query(Movie).all()

for movie in movies:

    print(
        movie.id,
        movie.title,
        movie.year
    )

session.close()
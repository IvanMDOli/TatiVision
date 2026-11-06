from app.models.database import SessionLocal
from app.models.movie import Movie


def main():
    with SessionLocal() as session:
        movies = session.query(Movie).all()

        for movie in movies:
            print(
                movie.id,
                movie.title,
                movie.year,
            )


if __name__ == "__main__":
    main()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_NAME = 'mood_tracker.sqlite'

"""Creating database."""
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Session = sessionmaker(bind=engine)

"""The class from which classes with tables inherit."""
Base = declarative_base()


"""Function for creating a database."""
# почему именно функция?
def create_db():
    Base.metadata.create_all(engine)

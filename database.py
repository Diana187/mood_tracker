from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_NAME = 'mood_tracker.sqlite'

"""Создаём базу данных"""
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Session = sessionmaker(bind=engine)

"""Класс, от которого наследуются классы с таблицами"""
Base = declarative_base()


"""Функция для создания БД"""
# почему именно функция?
def create_db():
    Base.metadata.create_all(engine)





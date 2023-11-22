from sqlalchemy import Column, Date, Integer, String, ForeignKey

from create_db import Base


class User(Base):
    __tablename__ = 'user_'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String)


class Mood(Base):
    __tablename__ = 'mood'

    mood_id = Column(Integer, primary_key=True)
    user_id = Column(String) # не разобралась со связями
    mood_rate = Column(Integer)
    description = Column(String)


class Tag(Base):
    __tablename__ = 'tag'

    tag_id = Column(Integer, primary_key=True)
    activity_name = Column(String)


class Record(Base):
    __tablename__ = 'record'

    record_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('user.id'))
    tag = Column(String, ForeignKey('tag.id'))
    mood = Column(String, ForeignKey('mood.id'))
    record_date = Column(Date)


class Records_to_tags(Base):
     __tablename__ = 'record_to_tag'

    # не разобралась со связями
     record_tag_id = Column(Integer, primary_key=True)
     record_id = Column(Integer)
     tag_id = Column(Integer)

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship #не совсем поняла как использовать

from database import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String)


class Mood(Base):
    __tablename__ = 'moods'

    mood_id = Column(Integer, primary_key=True)
    user_id = Column(String) # не разобралась со связями
    mood_rate = Column(Integer)
    description = Column(String)


class Tag(Base):
    __tablename__ = 'tags'

    tag_id = Column(Integer, primary_key=True)
    activity_name = Column(String)   #  ???
    tag_name = Column(String)


class Record(Base):
    __tablename__ = 'records'

    record_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    tag = Column(String, ForeignKey('tags.tag_id'))
    mood = Column(String, ForeignKey('moods.mood_id'))
    record_date = Column(Date)


# ?????
# class Records_to_tags(Base):
#      __tablename__ = 'records_to_tags'

#     # не разобралась со связями
#      record_tag_id = Column(Integer, primary_key=True)
#      record_id = Column(Integer)
#      tag_id = Column(Integer)

# нашла такое вот
record_tag_association = Table(
    'record_tag_association',
    Base.metadata,
    Column('record_id', Integer, ForeignKey('records.record_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'))
)

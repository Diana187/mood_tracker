import os

from sqlalchemy import and_

from database import DATABASE_NAME, Session
import create_database as db_creator
# from models import Mood, Record, Records_to_tags, User


if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        db_creator.create_database()

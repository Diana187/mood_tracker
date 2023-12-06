import os
import sqlite3

from sqlite3 import Error

from database import DATABASE_NAME
import create_database as db_creator


DATABASE_NAME = 'fake_db.sqlite'


def create_connection():
    conn = None
    # db_file =  Path().absolute() / Config.DB_FILE
    try:
        conn = sqlite3.connect(DATABASE_NAME)
    except Error as e:
        print(e)
    return conn

def setup_database():
    """Создаём соединение и курсор."""
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()

    """Создаём таблицу 'fake_db.sqlite'."""
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT,
            password TEXT
            );'''
        )
    
    """Создаём таблицу 'tags'."""
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS tags (
            tag_id INTEGER PRIMARY KEY,
            tag TEXT NOT NULL
            );'''
    )

    tags = [
    'Walk', 'Good sleep', 'Psychologist',
    'Meeting with friends', 'Sports', 'Reading a book',
    'Bad sleep', 'Alcohol', 'Overeating'
    ]

    # insert_tags = """INSERT INTO tags (item_id, location_id, volume, price) VALUES (?, ?, ?, ?);"""
    for tag in tags:
        cur.execute(
            '''INSERT INTO tags (tag) VALUES (?);''', (tag, )
        )

    """Create table 'moods'."""
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS moods (
        mood_id INTEGER PRIMARY KEY,
        mood_name TEXT NOT NULL,
        mood_rate INTEGER
        );'''
    )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':

    setup_database()

import os
import sqlite3
import random

from sqlite3 import Error

from database import DATABASE_NAME
import create_database as db_creator


DATABASE_NAME = 'fake_db.sqlite'
NUM_USERS = 5

def create_connection():
    conn = None
    # db_file =  Path().absolute() / Config.DB_FILE
    try:
        conn = sqlite3.connect(DATABASE_NAME)
    except Error as e:
        print(e)
    return conn

def setup_database():
    """Creating a connection and a cursor."""
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()

    """Creating table 'fake_db.sqlite'."""
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT,
            password TEXT
            );'''
    )

    lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam eget ligula eu lectus lobortis condimentum. Aliquam nonummy auctor massa. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nulla at risus. Quisque purus magna, auctor et, sagittis ac, posuere eu, lectus. Nam mattis, felis ut adipiscing.'
    
    lorem_ipsum_set  = set([i.strip(', .').capitalize() for i in lorem_ipsum.split(' ')])

    for username in random.sample(list(lorem_ipsum_set), NUM_USERS):
        cur.execute(
            '''INSERT INTO users (username) VALUES (?);''', (username, )
        )
    
    """Creating table 'tags'."""
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

    """Creating table 'moods'."""
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS moods (
            mood_id INTEGER PRIMARY KEY,
            mood_name TEXT NOT NULL,
            mood_rate INTEGER
            );'''
    )

    mood_rate = {'excellent': 2, 'good': 1, 'normal': 0, 'bad': -1, 'terrible': -2}

    for mood, rate in mood_rate.items():
        cur.execute(
            '''INSERT INTO moods (mood_name, mood_rate) VALUES (?, ?);''', (mood, rate, )
        )

    """Creating table 'records'."""
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS records (
            record_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            mood_id INTEGER,
            mood_description TEXT,
            activity TEXT,
            record_date DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (mood_id) REFERENCES moods(mood_id)
            );'''
    )

    for record in range(10):
        user_id = random.randint(1, 43)
        mood_id = random.randint(1, 5)
        cur.execute(
            '''INSERT INTO records (user_id, mood_id) VALUES (?, ?);''', (user_id, mood_id, )
        )

    # заполнять: рандомный int из диапозона от 1 до количества user (43), mood (5)
    # границы диапозона тоже должны входить 
    # заполнить record_date рандомный таймстамп из диапозона (смотри тг)

    """Creating table 'records_to_tags'."""
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS records_to_tags (
            record_tag_id INTEGER PRIMARY KEY,
            record_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (record_id) REFERENCES records(record_id),
            FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
            );'''
    )

    # NUMBER_OF_RECORDS; 



    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':

    setup_database()

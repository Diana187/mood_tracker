import os
import sqlite3
import random
from datetime import datetime, timedelta

from sqlite3 import Error

from database import DATABASE_NAME
import create_database as db_creator

import pandas as pd
import random
from faker import Faker

faker = Faker()


DATABASE_NAME = 'fake_db.sqlite'
NUM_USERS = 5
NUMBER_OF_RECORDS = 10
NUMBER_OF_RECORDS_TO_TAGS = NUMBER_OF_RECORDS * 3

# 5 users
# 9 tags
# 5 moods
# 10 records
# 30 records_to_tags

def create_connection():

    """Creates a connection to the database, a cursor, and returns them.
    If an error occurs, it prints it to the screen."""

    conn = None
    # db_file =  Path().absolute() / Config.DB_FILE
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cur = conn.cursor()
    except Error as e:
        print(e)
    return conn, cur

def setup_database(cur, conn, record_count=NUMBER_OF_RECORDS):

    """Creates table 'fake_db.sqlite', the 'users' table if it does not exist."""

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT,
            password TEXT
            );'''
    )

    # lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam eget ligula eu lectus lobortis condimentum. Aliquam nonummy auctor massa. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nulla at risus. Quisque purus magna, auctor et, sagittis ac, posuere eu, lectus. Nam mattis, felis ut adipiscing.'
    # lorem_ipsum_set  = set([i.strip(', .').capitalize() for i in lorem_ipsum.split(' ')])
    
    users = [f"{faker.unique.first_name()} {faker.unique.last_name()}" for _ in range(NUM_USERS)]
    emails = [f"{faker.email()}" for _ in range(NUM_USERS)]
    passwords = [f"{faker.password(length=5)}" for _ in range(NUM_USERS)]

    # Generating fake data for users
    for username, email, password in zip(users, emails, passwords):
        cur.execute(
        '''INSERT INTO users (username, email, password) VALUES (?, ?, ?);''', (username, email, password, )
        )

    # Creating table 'tags' if not exist
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
    # Создаём таблицу 'tags' и заполняем её тегами
    for tag in tags:
        cur.execute(
            '''INSERT INTO tags (tag) VALUES (?);''', (tag, )
        )

    # Creating table 'moods'
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
    
    """Filling the 'moods' table with various moods and mood ratings."""


    # Creating table 'records'.
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

    fake = Faker()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    for _ in range(record_count):
        user_id = random.randint(1, NUM_USERS)
        mood_id = random.randint(1, len(mood_rate))
        record_date = fake.date_time_between(start_date=start_date, end_date=end_date, ).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            '''INSERT INTO records (user_id, mood_id, record_date) VALUES (?, ?, ?);''', (user_id, mood_id, record_date, )
        )
    
    # Generate records for the 'records' table
    # Creating table 'records_to_tags'

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS records_to_tags (
            record_tag_id INTEGER PRIMARY KEY,
            record_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (record_id) REFERENCES records(record_id),
            FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
            );'''
    )

    """Filling the 'records_to_tags' table with test data."""

    for _ in range(NUMBER_OF_RECORDS_TO_TAGS):
        record_id = random.randint(1, record_count)
        tag_id = random.randint(1, len(tags))
        cur.execute(
        '''INSERT INTO records_to_tags (record_id, tag_id) VALUES (?, ?);''', (record_id, tag_id, )
        )

# Commit the changes
    
    conn.commit()



def create_query_string(query_params=None):

    """Takes a database connection and query parameters.
    Forms an SQL query to select records by username and tags."""

    placeholder = '?'
    placeholders = ', '.join([placeholder for _ in query_params['tags']])

    # Сreating a megaquery

    # это полный селект, но тут еще и фильтруем
    # sql = '''SELECT records.record_date, users.username, tags.tag, moods.mood_rate FROM records
    #     INNER JOIN records_to_tags ON records.record_id = records_to_tags.record_id
    #     INNER JOIN tags ON records_to_tags.tag_id = tags.tag_id
    #     INNER JOIN users ON records.user_id = users.user_id
    #     INNER JOIN moods ON records.mood_id = moods.mood_id
    #     WHERE users.username = ?
    #     AND tags.tag IN ({});'''.format(placeholders)

    sql_full = '''SELECT records.record_date, users.username, tags.tag, moods.mood_rate FROM records
        INNER JOIN records_to_tags ON records.record_id = records_to_tags.record_id
        INNER JOIN tags ON records_to_tags.tag_id = tags.tag_id
        INNER JOIN users ON records.user_id = users.user_id
        INNER JOIN moods ON records.mood_id = moods.mood_id
        WHERE'''
    
    sql_names = '''users.username = {}'''

    sql_tags = '''tags.tag IN ({})'''

    sql_time = '''records.record_date = ?'''

    sql_times = '''records.record_date BETWEEN ? AND ?'''


    # 
    if query_params.get('selected_name'):
        result_query = sql_full + sql_names.format(query_params['selected_name'])

    # # тут такой же полный селект + WHERE
    # sql_where = '''SELECT records.record_date, users.username, tags.tag, moods.mood_rate FROM records
    #     INNER JOIN records_to_tags ON records.record_id = records_to_tags.record_id
    #     INNER JOIN tags ON records_to_tags.tag_id = tags.tag_id
    #     INNER JOIN users ON records.user_id = users.user_id
    #     INNER JOIN moods ON records.mood_id = moods.mood_id
    #     WHERE
    #         users.username = ?
    #         AND
    #         records.record_date BETWEEN ? AND ?
    #     AND tags.tag IN ({});'''.format(placeholders)

    
    
    # sql_records = sql_whole + '''SELECT * FROM records WHERE record_date BETWEEN '2024-01-10' AND '2024-02-15';'''

# делаем в 2 шага, потому что методы работают inplace,
# если делаем так: args = [query_params['name'], ].extend(query_params['tags']), в args будет лежать None

    # args = [query_params['name'], ]
    # args.extend(query_params['tags'])

    # args = query_params['name'] + sql.format(placeholders)

    # cur = conn.execute(sql, args)
    cur = conn.execute(sql_whole)

    result = cur.fetchall()

    # print(result)
    return result


def get_all_tags():

    conn, cur = create_connection()

    # это строка
    sql_tag = '''SELECT * FROM tags;'''

    cur = conn.execute(sql_tag)
    result = cur.fetchall()
    filtered_result = [elem[1] for elem in result]
    cur.close()
    conn.close()

    return filtered_result


def regenerate_db(record_count=NUMBER_OF_RECORDS):
 
    filename = DATABASE_NAME
 
    if os.path.exists(filename):
        os.remove(filename)
        print(f"File {filename} removed.")
    else:
        print(f"File {filename} doesn't exist.")


    conn, cur = create_connection()
    setup_database(cur, conn, record_count)
    cur.close()
    conn.close()


if __name__ == '__main__':
    regenerate_db()
    conn, cur = create_connection()
    query_params = {
        'name': 'Derek Carter',
        'tags': ['Overeating', 'Alcohol', 'Meeting with friends', 'Psychologist', 'Walk']
    }
    query_database(conn, query_params, one_date)

    cur.close()
    conn.close()

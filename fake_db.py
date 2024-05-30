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

def create_connection():
    conn = None
    # db_file =  Path().absolute() / Config.DB_FILE
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cur = conn.cursor()
    except Error as e:
        print(e)
    return conn, cur

def setup_database(cur, conn):


    """Creating table 'fake_db.sqlite'."""
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

    for username, email, password in zip(users, emails, passwords):
        cur.execute(
        '''INSERT INTO users (username, email, password) VALUES (?, ?, ?);''', (username, email, password, )
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

    fake = Faker()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    for _ in range(NUMBER_OF_RECORDS):
        user_id = random.randint(1, NUM_USERS)
        mood_id = random.randint(1, len(mood_rate))
        record_date = fake.date_time_between(start_date=start_date, end_date=end_date, ).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            '''INSERT INTO records (user_id, mood_id, record_date) VALUES (?, ?, ?);''', (user_id, mood_id, record_date, )
        )

    """Creating table 'records_to_tags'."""
    # чтобы у одной записи могло быть много тегов
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS records_to_tags (
            record_tag_id INTEGER PRIMARY KEY,
            record_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (record_id) REFERENCES records(record_id),
            FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
            );'''
    )

    """Заполняем таблицу 'records_to_tags' тестовыми данными."""
    for _ in range(NUMBER_OF_RECORDS_TO_TAGS):
        record_id = random.randint(1, NUMBER_OF_RECORDS)
        tag_id = random.randint(1, len(tags))
        cur.execute(
        '''INSERT INTO records_to_tags (record_id, tag_id) VALUES (?, ?);''', (record_id, tag_id, )
        )
    
    conn.commit()


def query_database(conn, query_params):
# скармливать функции кварги, из них достанем список тегов и имя (в функцию неё приходит словарь)
# 
# написать кверю, которая выбирает times & moods и фильтрует по юзерам и по тегам
# потому что они будут в одном колбэке, а в нем два контрола: юзер и теги
# поселектить только нужные столбцы (например, id не нужен для датафрейма)
# поправить код  
# объединяю два запроса в один мегазапрос и параметризуем
# открываем апп2

# параметризовать теги, но их может быть несколько

# query = 'SELECT foo, bar, spam FROM the_table WHERE item_id IN ({}) ORDER BY item_id ASC'
# placeholder = '?'
# placeholders = ', '.join([placeholder for _ in ids])
# query.format(placeholders)
# 'SELECT foo, bar, spam FROM the_table WHERE item_id IN (?, ?, ?) ORDER BY item_id ASC'

    placeholder = '?'
    placeholders = ', '.join([placeholder for _ in query_params['tags']])


    """"Сreating a megaquery"""
    sql = '''SELECT records.record_date, users.username, tags.tag, moods.mood_rate FROM records
        INNER JOIN records_to_tags ON records.record_id = records_to_tags.record_id
        INNER JOIN tags ON records_to_tags.tag_id = tags.tag_id
        INNER JOIN users ON records.user_id = users.user_id
        INNER JOIN moods ON records.mood_id = moods.mood_id
        WHERE users.username = ?
        AND tags.tag IN ({});'''.format(placeholders)

# делаем в 2 шага, потому что методы работают inplace,
# если делаем так: args = [query_params['name'], ].extend(query_params['tags']), в args будет лежать None
    args = [query_params['name'], ]
    args.extend(query_params['tags'])
    # args = query_params['name'] + sql.format(placeholders)
    cur = conn.execute(sql, args)

    result = cur.fetchall()
    print(result)
    return result


    # """Creating a query that filters records falling within a certain time interval"""
    # cur.execute(
    #     '''SELECT * FROM records
    #         WHERE record_date BETWEEN '2024-01-10' AND '2024-02-15'
    #         ;'''
    # )
# параметризовать; раскопаем, когда будет слайдер



    # conn.commit()
    # cur.close()
    # conn.close()


if __name__ == '__main__':
    # собрать кишки в одну функцию regenerate_db; вызывать её под ифом и импортировать в ап 2
    conn, cur = create_connection()
    # setup_database(cur, conn)
    query_params = {
        'name': 'Derek Carter',
        'tags': ['Overeating', 'Alcohol', 'Meeting with friends', 'Psychologist', 'Walk']
    }
    query_database(conn, query_params)

    cur.close()
    conn.close()

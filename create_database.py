from faker import Faker

from database import create_db, Session

# from models import Mood, Record, record_tag_association, User


def create_database(load_fake_data: bool = True):
    create_db()
    if load_fake_data:
        _load_fake_data(Session())

def _load_fake_data(session: Session):
    predefined_tags = [
    'Walk', 'Good sleep', 'Psychologist',
    'Meeting with friends', 'Sports', 'Reading a book',
    'Bad sleep', 'Alcohol', 'Overeating'
    ]

# где-то будет
fake = Faker()

# тут что-то происхдит, генерятся фейковые данные

session = Session()

session.commit()
session.close()

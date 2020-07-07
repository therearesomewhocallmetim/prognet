import hashlib

from sqlalchemy import MetaData, create_engine

from polls.db import choice, question, users
from polls.settings import get_real_config

config = get_real_config('polls.yaml')

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[question, choice, users])

def sample_data(engine):
    conn = engine.connect()
    conn.execute(question.insert(), [
        {'question_text': "What's new?", 'pub_date': '2020-01-01 00:00:00'}
    ])
    conn.execute(choice.insert(), [
        {'choice_text': 'Not much', 'votes': 0, 'question_id': 1},
        {'choice_text': 'The sky', 'votes': 0, 'question_id': 1},
        {'choice_text': 'Just hacking again', 'votes': 0, 'question_id': 1},
    ])
    conn.execute(users.insert(), [
        {'login': 'admin', 'password': hashlib.sha3_256('password'.encode()).hexdigest()}
    ])
    conn.close()

if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)
    create_tables(engine)
    sample_data(engine)


import logging

from aiopg import sa
from sqlalchemy import MetaData, Integer, Column, Table, String, Date, ForeignKey

__all__ = ['question', 'choice']

meta = MetaData()

question = Table(
    'question', meta,
    Column('id', Integer, primary_key=True),
    Column('question_text', String(200), nullable=False),
    Column('pub_date', Date, nullable=False))

choice = Table(
    'choice', meta,
    Column('id', Integer, primary_key=True),
    Column('choice_text', String(200), nullable=False),
    Column('votes', Integer, server_default='0', nullable=False),
    Column(
        'question_id', Integer, ForeignKey('question.id', ondelete='CASCADE')))


async def init_pg(app):
    conf = app['config']['postgres']
    logging.warning(f'db port is {conf["port"]}')
    engine = await sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()

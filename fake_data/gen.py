import random
import string

from faker import Faker

from auth.models import User
from polls.models import Profile
from utils import database

fake = Faker('ru_RU')


def fake_data(length=10):
    """Generate fake data"""
    for _ in range(length):
        if random.choice((True, False)):
            person = _random_female()
        else:
            person = _random_male()
        yield person


async def generate(app):
    """Root function. Generate fake data and save to db"""
    async with database(app):
        async with app['db'].acquire() as conn:
            for user in fake_data(length=860_000):
                pk = await User.save(conn, login=user['login'], password=user['password'])
                user['user_id'] = pk
                await Profile.save(conn, user)
            await conn.commit()


def _random_male():
    return {
        'login': _login(),
        'password': '',
        'first_name': fake.first_name_male(),
        'last_name': fake.last_name_male(),
        'gender': 'male',
        'city': fake.city(),
        'interests': '\n'.join([_login(), _login(), _login()]),
        'birth': None,
    }


def _random_female():
    return {
        'login': _login(),
        'password': '',
        'first_name': fake.first_name_female(),
        'last_name': fake.last_name_female(),
        'gender': 'female',
        'city': fake.city(),
        'interests': '\n'.join([_login(), _login(), _login()]),
        'birth': None,
    }


def _login():
    return ''.join(random.choices(string.ascii_letters, k=10))



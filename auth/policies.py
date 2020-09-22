import random
import string
from base64 import b64encode, b64decode

import jwt
from aiohttp_security import AbstractAuthorizationPolicy, AbstractIdentityPolicy

try:
    from aiohttp_session import get_session
    HAS_AIOHTTP_SESSION = True
except ImportError:  # pragma: no cover
    HAS_AIOHTTP_SESSION = False



class SimpleAuthPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        return True


class JWTSessionIdentityPolicy(AbstractIdentityPolicy):

    def __init__(self, session_key='JWT_TOKEN'):
        self._session_key = session_key

        if not HAS_AIOHTTP_SESSION:  # pragma: no cover
            raise ImportError(
                'SessionIdentityPolicy requires `aiohttp_session`')

    async def identify(self, request):
        session = await get_session(request)
        token = session.get(self._session_key)
        return await identity_from_token(token)

    async def remember(self, request, response, identity, **kwargs):
        jwt_token = jwt.encode(
            {'identity': identity, 'random_string': ''.join(random.choices(string.ascii_letters, k=5))},
            'insecure_shared_secret', algorithm='HS256')

        session = await get_session(request)
        session[self._session_key] = b64encode(jwt_token).decode()

    async def forget(self, request, response):
        session = await get_session(request)
        session.pop(self._session_key, None)


async def identity_from_token(token):
    if not token:
        return None
    jwt_token = jwt.decode(
        b64decode(token.encode()),
        'insecure_shared_secret',
        algorithm='HS256')
    return jwt_token['identity']

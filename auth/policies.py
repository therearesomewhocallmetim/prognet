from aiohttp_security import AbstractAuthorizationPolicy


class SimpleAuthPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        return True


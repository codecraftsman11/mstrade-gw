from importlib import import_module
from .base import Auth
from ..exceptions import AuthError

__all__ = [
    'Auth',
    'auth'
]


def auth(auth_data):
    if 'params' not in auth_data:
        auth_data['params'] = auth_data
    if 'module' not in auth_data['driver']:
        mname = 'login'
    else:
        mname = auth_data['driver']['module']
    try:
        module = import_module('.' + mname, __name__)
    except Exception as exc:
        raise AuthError("Can't import auth module"
                        " {}. Details:{}".format(mname, exc))
    return module.Auth(auth_data['params'])

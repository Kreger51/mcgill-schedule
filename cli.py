#!env/bin/python

import os
from flask.ext.script import Manager, Shell, Server

from cronos import app, calminerva

os_env = os.environ
manager = Manager(app)


def echodir(a):
    print('\n'.join(x for x in dir(a) if not x.startswith('_')))


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'calminerva': calminerva, 'echodir': echodir}


@manager.command
def test():
    """Run the tests."""
    assert 'MINERVA_USER' in os_env
    assert 'MINERVA_SECRET' in os_env
    os.environ['CRONOS_ENV'] = 'test'
    import pytest
    exit_code = pytest.main(['tests', '--verbose'])
    return exit_code


manager.add_command('server', Server(port=8000))
manager.add_command('shell', Shell(make_context=_make_context))

if __name__ == '__main__':
    manager.run()

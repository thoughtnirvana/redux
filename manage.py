import subprocess as sp, os, signal, sys
import werkzeug.serving
from flask.ext.script import Manager, prompt_bool
import main

app = main.init()
manager = Manager(app)

from config import db

@manager.command
def run_tornado(port=5000):
    """
    Runs application under tornado.
    """
    import script.serve_app_tornado as runner
    signal.signal(signal.SIGINT, interrupt_handler)
    _runner(runner, port)

@manager.command
def run_gevent(port=5000):
    """
    Runs gevent server.
    """
    import gevent
    import script.serve_app_gevent as runner
    gevent.signal(signal.SIGINT, interrupt_handler)
    _runner(runner, port)

def _runner(runner, *args, **kwargs):
    environ = os.environ.get('FLASK_ENV')
    if not environ or environ != 'prod':
        # Run with reloading.
        @werkzeug.serving.run_with_reloader
        def run_server():
            runner.run_server(app, *args, **kwargs)
        run_server()
    else:
        runner.run_server(app, *args, **kwargs)

def interrupt_handler(*args, **kwargs):
    sys.exit(1)

@manager.command
def db_createall():
    "Creates database tables"
    db.create_all()

@manager.command
def db_dropall():
    "Drops all database tables"
    if prompt_bool("Are you sure ? You will lose all your data !"):
        db.drop_all()

@manager.command
def createapp(name):
    """
    Creates app template.
    """
    print sp.check_output('mkdir -p blueprints/%(name)s/templates/%(name)s' % locals(), shell=True),
    for static_dir in ('css', 'js', 'img'):
        print sp.check_output('mkdir -p blueprints/%(name)s/static/%(static_dir)s' % locals(), shell=True),
    for module in ('__init__.py', 'views.py', 'forms.py', 'models.py', 'urls.py'):
        print sp.check_output("touch blueprints/%(name)s/%(module)s" % locals(), shell=True),

@manager.command
def test():
    """
    Runs unit tests.
    """
    print sp.check_output('nosetests -v', shell=True),

@manager.command
def deps_get():
    """
    Installs dependencies.
    """
    print sp.check_output("pip install -r requirements.txt", shell=True),

@manager.command
def deps_update():
    """
    Updates dependencies.
    """
    print sp.check_output("pip install -r requirements.txt --upgrade", shell=True),

if __name__ == '__main__':
    manager.run()

import subprocess as sp, os, signal, sys
import werkzeug.serving
from werkzeug import import_string
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
    # create_all doesn't work if the models aren't imported
    import_string('models', silent=True)
    for blueprint_name, blueprint in app.blueprints.iteritems():
        import_string('%s.models' % blueprint.import_name, silent=True)
    db.create_all()

@manager.command
def db_dropall():
    "Drops all database tables"
    if prompt_bool("Are you sure ? You will lose all your data !"):
        db.drop_all()

@manager.command
def create_blueprint(name):
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

@manager.command
def create_model(name, rename=False, fields=''):
    """
    Creates model scaffold.
    """
    if '/' in name:
        blueprint_name, model_name = name.split('/')
        if rename:
            output_file = 'blueprints/%s/%s.py' % (blueprint_name, model_name.lower())
        else:
            output_file = 'blueprints/%s/models.py' % blueprint_name
    else:
        model_name = name
        if rename:
            output_file = '%s.py' % model_name.lower()
        else:
            output_file = 'models.py'
    model = create_model.model_scaffold % dict(model_name=model_name.capitalize())
    fields = fields.split()

    field_declares = []
    field_inits = []
    init_args = []
    for f in fields:
        splitted = f.split(':')
        if len(splitted) > 1:
            field_name, field_type = splitted[0], 'db.%s' % splitted[1]
        else:
            field_name, field_type = splitted[0], 'db.Text'
        field_declares.append(create_model.field_declare % dict(field_name=field_name, field_type=field_type))
        field_inits.append(create_model.field_init % dict(field_name=field_name))
        init_args.append(field_name)

    field_declares = '\n'.join(field_declares)

    init_args = (', %s' % ', '.join(init_args)) if init_args else ''
    init_body = '\n'.join(field_inits) if field_inits else '%spass' % (' ' * 8)
    init_method = '    def __init__(self%s):\n%s' % (init_args, init_body)

    with open(output_file, 'a') as out_file:
        model = '%(base)s%(field_declares)s\n\n%(init_method)s' % dict(base=model,
                                                                       field_declares=field_declares,
                                                                       init_method=init_method)
        out_file.write(model)

create_model.model_scaffold = '''

class %(model_name)s(db.Model):
    id = db.Column(db.Integer, primary_key=True)
'''
create_model.field_declare = '%s%%(field_name)s = db.Column(%%(field_type)s)' % (' ' * 4)
create_model.field_init = '%sself.%%(field_name)s = %%(field_name)s' % (' ' * 8)
create_model.init_method = '''
    def __init__(self%(args)s):
        %(body)s
'''

if __name__ == '__main__':
    manager.run()

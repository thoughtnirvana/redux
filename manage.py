from flask.ext.script import Manager, prompt_bool
import main

app = main.init()
manager = Manager(app)

from config import db

@manager.command
def createall():
    "Creates database tables"
    db.create_all()

@manager.command
def dropall():
    "Drops all database tables"
    if prompt_bool("Are you sure ? You will lose all your data !"):
        db.drop_all()

if __name__ == '__main__':
    manager.run()

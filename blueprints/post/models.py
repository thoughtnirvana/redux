from config import db

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

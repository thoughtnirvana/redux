from flaskext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from .models import Post

PostForm = model_form(Post, Form)

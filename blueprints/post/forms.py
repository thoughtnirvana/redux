from flaskext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
import models

PostForm = model_form(models.Post, Form)

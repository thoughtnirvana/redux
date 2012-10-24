import flaskext.wtf as wtf
from flaskext.wtf import Form, validators
from wtforms.ext.sqlalchemy.orm import model_form
import models


PostForm = model_form(models.Post, Form, field_args = {
    'name': {'validators': [validators.required()]},
    'title': {'validators': [validators.required(), validators.length(min=5)]},
    'content': {'validators': []},
    'tags': {'validators': []},
})

CommentForm = model_form(models.Comment, Form, field_args = {
    'commenter': {'validators': [validators.required()]},
    'body': {'validators': [validators.required()]},
})

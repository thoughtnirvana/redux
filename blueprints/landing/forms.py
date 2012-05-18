from flaskext.wtf import Form, PasswordField
from flaskext.wtf import Required, Email, Length
from flaskext.wtf.html5 import EmailField

class LoginForm(Form):
    email = EmailField('Email', description=u'Please enter email id',
                       validators=[Required(), Email()])
    password = PasswordField('Password', description=u'Please enter password',
                             validators=[Required(), Length(min=6, max=40)])

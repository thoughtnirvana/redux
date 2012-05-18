from .views import landing, login

routes = [
    ('/', 'landing', landing),
    ('/login', 'login', login, {'methods': ['GET', 'POST']}),
]

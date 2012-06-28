import views

routes = [
    ('/', 'index', views.post_index),
    ('/<int:id>', 'show', views.post_show),
    ('/new', 'new', views.post_new, {'methods': ['GET', 'POST']}),
    ('/<int:id>/edit', 'edit', views.post_edit, {'methods': ['GET', 'POST']}),
]

from flask import Blueprint
import config.urls as main_urls

__all__ = ['blueprint']

blueprint_name, blueprint_import_name = __name__.split('.')[-1], __name__
options = dict(static_folder='static', template_folder='templates', static_url_path='/static/%s' % blueprint_name)
blueprint = Blueprint(blueprint_name, blueprint_import_name, **options)
try:
    from .urls import routes
    main_urls.set_urls(blueprint, routes)
except ImportError, ex:
    pass

#!/usr/bin/env python
"""
Implements the main WSGI app. It instantiates and sets it up. It can
be run stand-alone as a flask application or it can be imported and
the resulting `app` object be used.
"""
import glob

from flask import Flask
from flask import Blueprint
from slimish_jinja import SlimishExtension
from werkzeug import import_string
from flask.ext.bcrypt import Bcrypt
from flask.ext.babel import Babel
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask.ext.debugtoolbar import DebugToolbarExtension


import config
import config.urls as urls
import config.settings as settings

def init():
    """
    Sets up flask application object `app` and returns it.
    """
    # Instantiate main app, load configs, register modules, set
    # url patterns and return the `app` object.
    app = Flask(__name__)
    app.config.from_object(settings)
    config.app = app
    # Init SQLAlchemy wrapper.
    config.db = SQLAlchemy(app)
    if app.debug:
        DebugToolbarExtension(app)
    #: Wrap the `app` with `Babel` for i18n.
    Babel(app)

    config.cache = Cache(app)
    app.jinja_env.add_extension(SlimishExtension)
    app.jinja_env.slim_debug = app.debug
    config.bcrypt = Bcrypt(app)
    # Other initializations.
    for fn, values in [(set_middlewares, getattr(settings, 'MIDDLEWARES', None)),
                        (set_context_processors, getattr(settings, 'CONTEXT_PROCESSORS', None)),
                        (set_template_filters, getattr(settings, 'TEMPLATE_FILTERS', None)),
                        (set_before_handlers, getattr(settings, 'BEFORE_REQUESTS', None)),
                        (set_after_handlers, getattr(settings, 'AFTER_REQUESTS', None)),
                        (set_log_handlers, getattr(settings, 'LOG_HANDLERS', None)),
                        (set_error_handlers, getattr(settings, 'ERROR_HANDLERS', None)),
                        (set_blueprints, getattr(settings, 'BLUEPRINTS', None))]:
        if values:
            fn(app, values)

    # Register all js and css files.
    assets = Environment(app)
    register_assets(app, assets)

    # URL rules.
    urls.set_urls(app)
    return app

def register_assets(app, assets):
    """
    Registers all css and js assets with `assets`
    """
    def _get_resource_files(static_folder, resource_folder, resource_ext):
        return [file[len(static_folder) + 1:] for file in
                glob.glob(static_folder + '/%s/*.%s' % (resource_folder, resource_ext))]

    def _get_css_files(static_folder):
        return _get_resource_files(static_folder, 'css', 'css')

    def _get_less_files(static_folder):
        return _get_resource_files(static_folder, 'css', 'less')

    def _get_js_files(static_folder):
        return _get_resource_files(static_folder, 'js', 'js')

    def _get_coffee_files(static_folder):
        return _get_resource_files(static_folder, 'js', 'coffee')

    def _append_blueprint_name(name, files):
        return ['%s/%s' % (name, f) for f in files]

    static_folder = app.static_folder
    css_files = _get_css_files(static_folder)
    less_files = _get_less_files(static_folder)
    js_files = _get_js_files(static_folder)
    coffee_files = _get_coffee_files(static_folder)

    for name, bp in app.blueprints.iteritems():
        if name == 'debugtoolbar':
            continue
        static_folder = bp.static_folder
        if static_folder:
            css_files.extend(_append_blueprint_name(name, _get_css_files(static_folder)))
            less_files.extend(_append_blueprint_name(name, _get_less_files(static_folder)))
            js_files.extend(_append_blueprint_name(name, _get_js_files(static_folder)))
            coffee_files.extend(_append_blueprint_name(name, _get_coffee_files(static_folder)))

    js_all = Bundle(Bundle(*js_files),
                    Bundle(*coffee_files, filters='coffeescript', output='js/coffee_all.js'),
                    filters='closure_js', output='js/application.js')
    assets.register('js_all', js_all)
    assets.register('js_all_compressed', js_all, filters='gzip', output='js/application.js.gz')

    css_all = Bundle(Bundle(*css_files),
                     Bundle(*less_files, filters='less', output='css/less_all.css'),
                     filters='cssmin', output='css/application.css')
    assets.register('css_all', css_all)
    assets.register('css_all_compressed', css_all, filters='gzip', output='css/application.css.gz')

def set_middlewares(app, middlewares):
    """
    Adds middlewares to the app.
    """
    # Add middlewares.
    if middlewares:
        for m in middlewares:
            if isinstance(m, list) or isinstance(m, tuple):
                if len(m) == 3:
                    mware, args, kwargs = m
                    new_mware = mware(app.wsgi_app, *args, **kwargs)
                elif len(mware) == 2:
                    mware, args = m
                    if isinstance(args, dict):
                        new_mware = mware(app.wsgi_app, **args)
                    elif isinstance(args, list) or isinstance(args, tuple):
                        new_mware = mware(app.wsgi_app, *args)
                    else:
                        new_mware = mware(app.wsgi_app, args)
            else:
                new_mware = m(app.wsgi_app)
            app.wsgi_app = new_mware

def set_blueprints(app, blueprints):
    """
    Registers blueprints with the app.
    """
    # Register blueprints.
    for blueprint in blueprints:
        url_prefix = None
        if len(blueprint) == 2:
            blueprint, url_prefix = blueprint
        blueprint_object = import_string('%s:BLUEPRINT' % blueprint, silent=True)
        if not blueprint_object:
            blueprint_name, blueprint_import_name = blueprint.split('.')[-1], blueprint
            static_url_path = '/static' if url_prefix else '/static/%s' % blueprint_name
            options = dict(static_folder='static', template_folder='templates',
                           static_url_path=static_url_path)
            blueprint_object = Blueprint(blueprint_name, blueprint_import_name, **options)
        blueprint_routes = import_string('%s.urls:routes' % blueprint_import_name, silent=True)
        if blueprint_routes:
            urls.set_urls(blueprint_object, blueprint_routes)

        # Other initializations.
        for fn, values in [(set_before_handlers, import_string('%s:BEFORE_REQUESTS' % blueprint, silent=True)),
                           (set_before_app_handlers, import_string('%s:BEFORE_APP_REQUESTS' % blueprint, silent=True)),
                           (set_after_handlers, import_string('%s:AFTER_REQUESTS' % blueprint, silent=True)),
                           (set_after_app_handlers, import_string('%s:AFTER_APP_REQUESTS' % blueprint, silent=True)),
                           (set_context_processors, import_string('%s:CONTEXT_PROCESSORS' % blueprint, silent=True)),
                           (set_app_context_processors, import_string('%s:APP_CONTEXT_PROCESSORS' % blueprint, silent=True)),
                           (set_error_handlers, import_string('%s:ERROR_HANDLERS' % blueprint, silent=True)),
                           (set_app_error_handlers, import_string('%s:APP_ERROR_HANDLERS' % blueprint, silent=True))]:
            if values:
                fn(app, values)
        # Can be mounted at specific prefix.
        if url_prefix:
            app.register_blueprint(blueprint_object, url_prefix=url_prefix)
        else:
            app.register_blueprint(blueprint_object)

def set_before_handlers(app, before_handlers):
    """
    Sets before handlers.
    """
    # Register before request middlewares.
    for before in before_handlers:
        before = app.before_request(before)

def set_before_app_handlers(app, before_handlers):
    """
    Sets before handlers.
    When called from a blueprint, works on the application level rather than blueprint level.
    """
    # Register before request middlewares.
    for before in before_handlers:
        before = app.before_app_request(before)

def set_after_handlers(app, after_handlers):
    """
    Sets after handlers.
    """
    # Register before request middlewares.
    for after in after_handlers:
        after = app.after_request(after)

def set_after_app_handlers(app, after_handlers):
    """
    Sets after handlers.
    When called from a blueprint, works on the application level rather than blueprint level.
    """
    # Register before request middlewares.
    for after in after_handlers:
        after = app.after_app_request(after)

def set_log_handlers(app, log_handlers):
    """
    Sets log handlers for the app.
    """
    # Set log handlers.
    for handler in log_handlers:
        app.logger.addHandler(handler)

def set_template_filters(app, template_filters):
    """
    Sets jinja2 template filters.
    """
    for filter_name, filter_fn in template_filters:
        app.jinja_env.filters[filter_name] = filter_fn

def set_context_processors(app, context_processors):
    """
    Sets jinja2 context processors.
    """
    app.context_processor(lambda: context_processors)

def set_app_context_processors(app, context_processors):
    """
    Sets jinja2 context processors.
    When called from a blueprint, works on the application level rather than blueprint level.
    """
    app.app_context_processor(lambda: context_processors)

def set_error_handlers(app, error_handlers):
    """
    Sets error handlers.
    """
    for code, fn in error_handlers:
        fn = app.errorhandler(code)(fn)

def set_app_error_handlers(app, error_handlers):
    """
    Sets error handlers.
    When called from a blueprint, works on the application level rather than blueprint level.
    """
    for code, fn in error_handlers:
        fn = app.app_errorhandler(code)(fn)

app = init()
if __name__ == '__main__':
    #: Create the `app` object via :func:`init`. Run the `app`
    #: if called standalone.
    app.run()
